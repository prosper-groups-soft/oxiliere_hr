# Sécurité applicative

> **Pratiques et standards** pour garantir que le code, les dépendances et l'infrastructure sont protégés contre les vulnérabilités courantes.

> ⚠️ **Document transverse** — Les pratiques de sécurité s'intègrent dans tous les autres piliers (code, CI/CD, reviews). Ce document centralise les règles communes.

---

## Quickstart

```bash
# Scanner les dépendances
npm audit
npx snyk test

# Linting de sécurité
npx eslint --rulesdir eslint-plugin-security

# Scanner le code (SAST)
npx semgrep --config=auto src/
```

---

## Table des matières

1. [Philosophie](#1-philosophie)
2. [Principes généraux](#2-principes-généraux)
3. [OWASP Top 10 pour le web](#3-owasp-top-10-pour-le-web)
4. [Sécurité des dépendances](#4-sécurité-des-dépendances)
5. [SAST — Static Analysis Security Testing](#5-sast--static-analysis-security-testing)
6. [Gestion des secrets](#6-gestion-des-secrets)
7. [Sécurité dans le code](#7-sécurité-dans-le-code)
8. [Sécurité dans la CI/CD](#8-sécurité-dans-la-cicd)
9. [Sécurité dans les reviews](#9-sécurité-dans-les-reviews)
10. [Gestion des incidents de sécurité](#10-gestion-des-incidents-de-sécurité)
11. [Anti-patterns](#11-anti-patterns)

---

## 1. Philosophie

> **La sécurité n'est pas une fonctionnalité — c'est une propriété du système.**

Nos principes :

1. **La sécurité se conçoit dès le départ** — Pas de « on ajoutera la sécurité plus tard ». Le métamodèle et l'architecture doivent intégrer les contraintes de sécurité.
2. **Défense en profondeur** — Plusieurs couches de protection, jamais une seule.
3. **Moindre privilège** — Chaque composant, chaque utilisateur, chaque service n'a que les droits strictement nécessaires.
4. **Sécurité par défaut** — Les valeurs par défaut sont toujours les plus sûres.
5. **Ne pas inventer la cryptographie** — Utiliser des bibliothèques standards et éprouvées.

---

## 2. Principes généraux

### 2.1 Règles d'or

| Règle | Description |
|-------|-------------|
| **Jamais de confiance implicite** | Toujours valider, toujours authentifier |
| **Jamais de secrets dans le code** | Clés, tokens, mots de passe → coffre de secrets |
| **Jamais d'entrée non validée** | Toute donnée entrante est potentiellement malveillante |
| **Jamais de sortie non échappée** | Toute donnée affichée peut être une XSS |
| **Journaliser, toujours** | Toute action sensible doit être tracée |

### 2.2 Surface d'attaque

Connaître les points d'entrée potentiels de votre application :

```
[ Navigateur ] ──→ [ API / Backend ] ──→ [ Base de données ]
      │                    │                      │
  XSS, CSRF           Injection,               SQLi,
  Clickjacking         Auth bypass              Data leak
      │                    │                      │
      ▼                    ▼                      ▼
  [ CDN / DNS ]      [ Services tiers ]    [ Stockage fichiers ]
      │                    │                      │
  Cache poisoning     API keys leak           Path traversal
  Subdomain take.     Man-in-the-middle
```

---

## 3. OWASP Top 10 pour le web

Les 10 vulnérabilités les plus critiques, adaptées à notre contexte.

| # | Vulnérabilité | Risque | Prévention |
|---|---------------|--------|------------|
| 1 | **Broken Access Control** | Un utilisateur accède à des données d'un autre | Vérifier les permissions à chaque accès, pas seulement dans l'UI |
| 2 | **Cryptographic Failures** | Données sensibles en clair | Chiffrer en transit (HTTPS) et au repos (BDD) |
| 3 | **Injection** (SQL, NoSQL, OS) | Exécution de commandes non prévues | Utiliser des ORM, paramétrer les requêtes, ne jamais concaténer |
| 4 | **Insecure Design** | Fail de conception (pas de code) | Menée de conception, threat modeling en amont |
| 5 | **Security Misconfiguration** | Confs par défaut, pages exposées | Durcir la configuration, désactiver ce qui n'est pas utilisé |
| 6 | **Vulnerable Components** | Dépendances avec CVE connues | `npm audit`, Dependabot, mise à jour régulière |
| 7 | **Auth Failures** | Session faible, MFA absent | MFA obligatoire, session timeout, refresh tokens |
| 8 | **Data Integrity Failures** | Mise à jour non vérifiée | Signer les artefacts, vérifier les intégrités (SRI) |
| 9 | **Logging & Monitoring Failures** | Incident non détecté | Logs structurés, alerting, audit trail |
| 10 | **SSRF** | Le serveur fait des requêtes vers l'interne | Whitelist des URLs, validation des entrées |

### 3.1 Focus Oxilière : les risques les plus probables

Pour une application RH comme Oxilière :

| Risque | Impact | Priorité |
|--------|--------|----------|
| 🔴 Accès non autorisé aux données employés | RGPD, données personnelles | **Critique** |
| 🟠 Injection SQL / NoSQL | Vol de données | **Haute** |
| 🟠 XSS | Usurpation de session | **Haute** |
| 🟡 Dépendances vulnérables | Prise de contrôle | **Moyenne** |
| 🟡 Fuite de secrets (API keys) | Accès aux services externes | **Moyenne** |

---

## 4. Sécurité des dépendances

### 4.1 Règles

- **Audit régulier** — `npm audit` exécuté à chaque CI
- **Mises à jour automatiques** — Dependabot / Renovate activé pour les patches de sécurité
- **Limiter les dépendances** — Pas de bibliothèque pour une fonction utilitaire de 5 lignes
- **Épurer les dépendances inutilisées** — `depcheck` régulièrement

### 4.2 Gestion des CVE

| Gravité | Délai de correction | Action |
|---------|---------------------|--------|
| 🔴 Critique | < 48h | Mise à jour immédiate, hotfix si nécessaire |
| 🟠 Haute | < 1 semaine | Planifier dans le sprint en cours |
| 🟡 Moyenne | < 1 mois | Planifier dans les prochains sprints |
| 🔵 Basse | < 3 mois | Planifier quand possible |

### 4.3 Scripts CI

```yaml
security-audit:
  runs-on: ubuntu-latest
  steps:
    - run: npm ci
    - run: npm audit --audit-level=high
    - run: npx snyk test --severity-threshold=high
```

> [!IMPORTANT]
> Un échec de `npm audit` sur une vulnérabilité haute ou critique **bloque le merge**. Pas de PR acceptée avec une dépendance vulnérable connue.

---

## 5. SAST — Static Analysis Security Testing

### 5.1 Outils

| Outil | Usage | Exécution |
|-------|-------|-----------|
| **Semgrep** | Analyse statique de sécurité | CI (PR) |
| **ESLint avec plugin security** | Détection de patterns dangereux | CI (PR) |
| **Trivy** | Scan des conteneurs (Docker) | CI (build) |

### 5.2 Patterns détectés par Semgrep

```yaml
# Exemple de règles Semgrep
rules:
  - id: no-raw-sql
    pattern: |
      db.query("SELECT ..." + $USER_INPUT)
    message: "Ne pas concaténer des entrées utilisateur dans SQL"
    severity: ERROR

  - id: no-hardcoded-secret
    pattern: |
      const $SECRET = "..."
    patterns:
      - metavariable-regex:
          metavariable: $SECRET
          regex: (password|secret|key|token)
    severity: WARNING
```

---

## 6. Gestion des secrets

### 6.1 Où stocker les secrets

| Type | Stockage |
|------|----------|
| Clés API / tokens | GitHub Secrets / Vault |
| Variables d'environnement | `.env` local (jamais commité) |
| Certificats | Coffre dédié (Hashicorp Vault) |
| Secrets de BDD | Variables d'environnement CI/CD |

### 6.2 Règles

- **.gitignore** contient toujours `.env`, `.env.local`, `*.key`, `*.pem`
- **Pré-commit hook** vérifie qu'aucun secret n'est commité (ex: `git-secrets`)
- **Rotation des secrets** — Changement tous les 90 jours pour les clés d'API
- **Jamais de secret en dur** — Ni dans le code, ni dans les commentaires, ni dans les logs

### 6.3 Exemple

```typescript
// ❌ MAUVAIS : secret en dur
const apiKey = 'sk_live_1234567890abcdef';

// ✅ BON : variable d'environnement
const apiKey = import.meta.env.VITE_STRIPE_API_KEY;

// ✅ MEILLEUR : passé via le pipeline CI/CD
const apiKey = process.env.STRIPE_API_KEY;  // jamais exposé au client
```

---

## 7. Sécurité dans le code

### 7.1 Validation des entrées

- **Toujours valider** côté serveur (la validation côté client est un confort, pas une sécurité)
- **Utiliser un schéma de validation** (Zod, Yup) — pas de validation ad-hoc
- **Échapper les sorties** — Ne jamais afficher de données utilisateur brutes dans le HTML

```typescript
// Exemple avec Zod
const LeaveRequestSchema = z.object({
  employeeId: z.string().uuid(),
  startDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  endDate: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  type: z.enum(['annual', 'sick', 'unpaid']),
});

function createLeave(input: unknown) {
  const validated = LeaveRequestSchema.parse(input); // Valide ET type-safe
  // ... logique métier
}
```

### 7.2 Contrôle d'accès

- **Vérifier les permissions à chaque couche** — Pas seulement dans l'UI
- **Principe de l'utilisateur connecté** — Ne jamais utiliser l'ID d'un utilisateur passé dans l'URL
- **Journaliser les accès aux données sensibles**

```typescript
// ❌ MAUVAIS : l'ID vient de l'URL, peut être modifié
async function loadEmployee(id: string) {
  return db.employee.find(id);  // Pas de vérification des droits
}

// ✅ BON : l'ID vient de la session
async function loadEmployee(id: string) {
  const currentUser = getCurrentUser();
  if (!canAccessEmployee(currentUser, id)) {
    throw new ForbiddenError();
  }
  return db.employee.find(id);
}
```

### 7.3 Protection CSRF

- Utiliser des tokens CSRF pour les formulaires
- Vérifier l'en-tête `Origin` / `Referer` pour les requêtes API
- Ne pas utiliser de cookies d'authentification sans SameSite=Strict

### 7.4 Headers de sécurité

```typescript
// Exemple SvelteKit : ajouter les headers de sécurité
export function handle({ event, resolve }) {
  const response = await resolve(event);
  response.headers.set('Content-Security-Policy', "default-src 'self'");
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('Strict-Transport-Security', 'max-age=31536000');
  return response;
}
```

---

## 8. Sécurité dans la CI/CD

- **Scan SAST** sur chaque PR (Semgrep)
- **Audit des dépendances** (`npm audit`) en CI
- **Pas de secret dans les logs CI** — GitHub Actions masque automatiquement les secrets, mais vérifier
- **Image Docker scannée** (Trivy) avant déploiement
- **Signature des artefacts** si déploiement en production

---

## 9. Sécurité dans les reviews

La checklist de [Code Review](code-review.md) intègre ces points :

- [ ] Les entrées utilisateur sont-elles validées côté serveur ?
- [ ] Les accès sont-ils vérifiés (pas seulement dans l'UI) ?
- [ ] Y a-t-il des secrets en dur dans le code ?
- [ ] Les dépendances ajoutées sont-elles nécessaires ?
- [ ] Les logs ne contiennent-ils pas de données sensibles ?

---

## 10. Gestion des incidents de sécurité

### 10.1 Procédure

| Étape | Action | Responsable |
|-------|--------|-------------|
| 1 | **Détection** — Incident signalé (CI, monitoring, utilisateur) | N'importe qui |
| 2 | **Qualification** — Confirmer que c'est une vraie vulnérabilité | Lead dev |
| 3 | **Containment** — Limiter l'impact (désactiver une feature, révoquer des tokens) | Lead dev |
| 4 | **Correction** — Patch, hotfix, mise à jour | Développeur |
| 5 | **Vérification** — Confirmer que le correctif fonctionne | Reviewer |
| 6 | **Post-mortem** — Analyser pourquoi l'incident a eu lieu, comment l'éviter | Équipe |

### 10.2 Canaux

- **Signalement** : Issue GitHub avec label `security`
- **Urgent** : Message direct sur le canal d'équipe
- **Critique** : Appel téléphonique + hotfix immédiat

---

## 11. Anti-patterns

### Anti-pattern 1 : Sécurité par l'obscurité

**Symptôme** : « Si on cache l'URL, personne ne la trouvera. »

**Solution** : La sécurité ne repose jamais sur la discrétion. Authentification, autorisation, chiffrement — toujours.

### Anti-pattern 2 : Validation uniquement côté client

**Symptôme** : Les données sont validées dans le navigateur mais pas sur le serveur.

**Solution** : La validation côté serveur est **obligatoire**. Le client est un environnement non fiable.

### Anti-pattern 3 : Secrets partout

**Symptôme** : 20 clés API différentes, 5 mots de passe stockés en variable d'environnement, 3 tokens en dur.

**Solution** : Mutualiser les services, limiter le nombre de secrets, utiliser un coffre central.

### Anti-pattern 4 : Ignorer les alertes de dépendances

**Symptôme** : Dependabot ouvre des PR mais personne ne les merge.

**Solution** : Une alerte de sécurité est prioritaire sur toute feature. Si le correctif casse quelque chose, le bug est dans le code, pas dans le correctif.

---

> **Dernier conseil** : La sécurité n'est jamais « finie ». C'est un processus continu : nouvelles vulnérabilités découvertes, nouvelles dépendances, nouveau code. Intégrez la sécurité dans votre quotidien (CI, reviews, audits réguliers) plutôt que d'en faire un audit ponctuel stressant.
