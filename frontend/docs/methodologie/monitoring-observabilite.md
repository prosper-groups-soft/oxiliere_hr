# Monitoring et Observabilité

> **Pratiques pour comprendre ce qui se passe dans l'application en production** : logs, métriques, alertes et traçabilité.

> ⚠️ **Document transverse** — Le monitoring s'appuie sur ce qui a été conçu et livré. Il n'ajoute pas de fonctionnalité métier mais garantit qu'on peut détecter et diagnostiquer les problèmes.

---

## Quickstart

```typescript
// Log structuré
console.log(JSON.stringify({
  level: 'info',
  event: 'leave.submitted',
  employeeId: 'EMP-123',
  duration: 42
}));

// Health check
fetch('/api/health').then(r => r.json()).then(console.log);
```

---

## Table des matières

1. [Philosophie](#1-philosophie)
2. [Les 3 piliers de l'observabilité](#2-les-3-piliers-de-lobservabilité)
3. [Logs structurés](#3-logs-structurés)
4. [Métriques](#4-métriques)
5. [Alerting](#5-alerting)
6. [Health checks](#6-health-checks)
7. [Traçabilité et audit](#7-traçabilité-et-audit)
8. [Monitoring dans le cycle de vie](#8-monitoring-dans-le-cycle-de-vie)
9. [Anti-patterns](#9-anti-patterns)

---

## 1. Philosophie

> **Si ça n'est pas monitoré, ça n'existe pas.**

Nos principes :

1. **Tout ce qui peut planter doit être surveillé** — Si un service peut tomber, on doit le savoir avant les utilisateurs.
2. **Les logs sont des données structurées** — Pas de `console.log("Toto a cliqué sur le bouton")`.
3. **Pas d'alertes inutiles** — Chaque alerte doit déclencher une action. Une alerte ignorée est pire que pas d'alerte.
4. **L'observabilité sert le diagnostic** — Le but n'est pas de collecter des données, mais de pouvoir répondre à « Que s'est-il passé ? » rapidement.

---

## 2. Les 3 piliers de l'observabilité

```
┌────────────────────────────────────────────────────────────┐
│                     OBSERVABILITÉ                           │
│                                                            │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────────────┐  │
│  │   LOGS      │  │  MÉTRIQUES  │  │    TRACES          │  │
│  │             │  │             │  │                    │  │
│  │ Événements  │  │ Compteurs   │  │ Requête complète   │  │
│  │ Erreurs     │  │ Durées      │  │ Parcours inter-    │  │
│  │ Contexte    │  │ Taux        │  │ services           │  │
│  └─────────────┘  └─────────────┘  └───────────────────┘  │
│                                                            │
│  Question :      │  Question :       │  Question :         │
│  « Que s'est-    │  « Combien de     │  « Où est le        │
│    il passé ? »  │    requêtes ? »   │    goulot ? »       │
└────────────────────────────────────────────────────────────┘
```

---

## 3. Logs structurés

### 3.1 Format

Tous les logs sont au format JSON structuré, avec des champs communs :

```json
{
  "timestamp": "2026-07-13T10:30:00.000Z",
  "level": "info",
  "event": "leave.submitted",
  "service": "api",
  "environment": "production",
  "duration_ms": 42,
  "metadata": {
    "employeeId": "EMP-123",
    "requestId": "req_abc123"
  },
  "error": null
}
```

### 3.2 Niveaux de log

| Niveau | Usage | Exemple |
|--------|-------|---------|
| `debug` | Développement, détaillé | « Champ X validé avec valeur Y » |
| `info` | Événements normaux importants | « Demande de congé soumise » |
| `warn` | Anomalie non bloquante | « Temps de réponse > 1s » |
| `error` | Erreur bloquante | « Échec de validation du solde » |
| `fatal` | Crash applicatif | « Impossible de se connecter à la BDD » |

### 3.3 Ce qu'il faut logger

✅ À logger :
- Actions utilisateur importantes (création, modification, suppression)
- Échecs d'authentification
- Appels API avec leurs temps de réponse
- Erreurs inattendues

❌ À ne PAS logger :
- Mots de passe, tokens, clés (même masqués partiellement)
- Données personnelles au complet
- Corps de requêtes volumineux (> 1 KB de données non essentielles)
- Logs de debug en production

### 3.4 Exemples

```typescript
// ✅ Bon log structuré
console.log(JSON.stringify({
  level: 'info',
  event: 'leave.submitted',
  service: 'conges',
  employeeId: request.employeeId,
  duration_ms: Date.now() - start,
}));

// ❌ Mauvais log
console.log('Demande de congés soumise');
console.log('Employee:', request);  // Risque RGPD
```

---

## 4. Métriques

### 4.1 Métriques clés

| Catégorie | Métrique | Seuil d'alerte |
|-----------|----------|----------------|
| **Traffic** | Requêtes par minute | > 2x la normale |
| **Erreurs** | Taux d'erreur HTTP (4xx, 5xx) | > 1% de 5xx |
| **Latence** | Temps de réponse p95 | > 2s |
| **Saturation** | Utilisation CPU / Mémoire | > 80% |
| **Business** | Congés créés / jour | Chute > 50% |

### 4.2 Types de métriques

```
# RED Method (pour les services)
Rate    → Requêtes par seconde
Errors  → Nombre d'erreurs
Duration→ Temps de réponse

# USE Method (pour les ressources)
Utilization → Taux d'utilisation
Saturation  → File d'attente
Errors      → Erreurs
```

---

## 5. Alerting

### 5.1 Règles d'alerte

| Sévérité | Délai de réponse | Canal | Exemple |
|-----------|------------------|-------|---------|
| 🔴 **P1 — Critique** | Immédiat | Appel / SMS | API inaccessible, aucun utilisateur ne peut se connecter |
| 🟠 **P2 — Haute** | < 30 min | Slack + notif | Taux d'erreur > 5%, temps de réponse > 3s |
| 🟡 **P3 — Moyenne** | < 4h | Slack | Utilisation CPU > 80%, erreur sur un sous-système non critique |
| 🔵 **P4 — Basse** | < 48h | Issue GitHub | Dépendance obsolète, warning dans les logs |

### 5.2 Anti-pattern d'alerte

```text
❌ « CPU > 50% » → alerte trop fréquente, ignorée au bout de 2 jours
✅ « CPU > 80% pendant 5 minutes » → alerte utile
```

> [!WARNING]
> **Fatigue d'alerte** : Si vous recevez plus de 3 alertes par jour qui ne nécessitent pas d'action immédiate, vos règles sont trop larges. Une alerte qui n'est jamais suivie d'action doit être supprimée ou redéfinie.

---

## 6. Health checks

### 6.1 Point de terminaison

```typescript
// GET /api/health
{
  "status": "healthy",         // healthy | degraded | unhealthy
  "version": "1.2.0",
  "uptime": 123456,
  "checks": {
    "database": { "status": "healthy", "latency_ms": 5 },
    "api_externe": { "status": "healthy", "latency_ms": 120 },
    "memory": { "status": "healthy", "usage_percent": 45 }
  }
}
```

### 6.2 Types de health checks

| Check | Fréquence | Action si échec |
|-------|-----------|-----------------|
| **Liveness** | Toutes les 30s | Redémarrer le conteneur |
| **Readiness** | Toutes les 10s | Retirer du pool de requêtes |
| **Startup** | Au démarrage | Attendre avant d'envoyer du traffic |

---

## 7. Traçabilité et audit

Toute action sensible (création, modification, suppression de données, connexion, déconnexion) doit être tracée :

```typescript
interface AuditEntry {
  event: string;          // 'leave.approved'
  actor: string;          // 'manager@example.com'
  action: string;         // 'approve'
  resource: string;       // 'LeaveRequest'
  resourceId: string;     // 'LEAVE-2024-042'
  timestamp: string;      // ISO date
  metadata: Record<string, unknown>;  // Contexte additionnel
}
```

Les logs d'audit sont :
- **Conservés** 1 an minimum (conformité RGPD)
- **Immutables** (écriture seule, pas de suppression)
- **Horodatés** précisément
- **Reliables** aux sessions utilisateur

---

## 8. Monitoring dans le cycle de vie

| Phase | Monitoring associé |
|-------|-------------------|
| **Conception** | Définir les événements métier à tracer (cf. métamodèle) |
| **Développement** | Logs structurés, métriques locales |
| **Review** | Vérifier que les événements critiques sont loggés |
| **CI/CD** | Health check après déploiement, smoke tests |
| **Production** | Alerting, dashboards, audits |

---

## 9. Anti-patterns

### Anti-pattern 1 : Trop de logs, trop de bruit

**Symptôme** : Des milliers de logs par minute, impossibles à exploiter.

**Solution** : Distinguer logs de debug (en local) et logs de prod (événements importants seulement). Utiliser les niveaux correctement.

### Anti-pattern 2 : Pas de logs du tout

**Symptôme** : Une erreur en production, aucun log pour comprendre pourquoi.

**Solution** : Au minimum, logger les entrées/sorties des API, les échecs, les actions utilisateur importantes.

### Anti-pattern 3 : Alerter sans seuil

**Symptôme** : « CPU > 10% » → alerte toutes les 5 minutes.

**Solution** : Seuils avec durée minimum. Une alerte doit signifier un problème réel, pas une fluctuation normale.

### Anti-pattern 4 : Données personnelles dans les logs

**Symptôme** : Logs contenant des adresses email, téléphones, numéros de sécurité sociale en clair.

**Solution** : Structurer les logs pour exclure les champs sensibles. Utiliser des identifiants plutôt que des données personnelles.

---

> **Dernier conseil** : L'observabilité n'est pas un outil — c'est une pratique. Elle commence à la conception (quels événements tracer ?) et s'affine en production (quelles alertes sont vraiment utiles ?). Investissez-y progressivement : d'abord les logs, puis les métriques clés, enfin l'alerting.
