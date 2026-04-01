<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Badge } from "@/components/ui/badge";
  import { Button } from "@/components/ui/button";
  import { Card, CardContent } from "@/components/ui/card";

  let { resumeUrl } = $props<{ resumeUrl?: string }>();

  let isLoading = $state(false);
  let error = $state<string | null>(null);

  // Handle file download
  async function handleDownload() {
    if (!resumeUrl) return;
    
    isLoading = true;
    error = null;
    
    try {
      // Create download link
      const link = document.createElement('a');
      link.href = resumeUrl;
      link.download = resumeUrl.split('/').pop() || 'resume.pdf';
      link.target = '_blank';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (err) {
      error = 'Erreur lors du téléchargement';
      console.error('Download error:', err);
    } finally {
      isLoading = false;
    }
  }

  // Handle file preview in new tab
  function handlePreview() {
    if (!resumeUrl) return;
    
    window.open(resumeUrl, '_blank');
  }

  // Get file info
  function getFileInfo() {
    if (!resumeUrl) return null;
    
    const urlParts = resumeUrl.split('/');
    const fileName = urlParts[urlParts.length - 1];
    const fileExtension = fileName.split('.').pop()?.toUpperCase();
    
    return {
      name: fileName,
      extension: fileExtension || 'PDF',
      size: '2.3 MB' // Mock size - in real app, this would come from the file metadata
    };
  }

  const fileInfo = $derived(getFileInfo());
</script>


<div class="space-y-4">
  {#if !resumeUrl}
    <div class="text-center py-8 border-2 border-dashed border-slate-300 rounded-lg">
      <AppIcon name="file" size={34} class="text-slate-300 mx-auto mb-3" strokeWidth={1.2} />
      <p class="text-slate-500 mb-1 text-[0.9rem]">Aucun CV disponible</p>
      <p class="text-sm text-slate-400 text-[0.83rem]">Le CV n'a pas été uploadé pour ce candidat</p>
    </div>
  {:else}
    <!-- File Info Card -->
    <Card class="border-slate-200">
      <CardContent class="p-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="h-12 w-12 bg-red-50 border border-red-200 rounded-lg flex items-center justify-center">
              <AppIcon name="file" size={20} class="text-red-600" />
            </div>
            <div>
              <h4 class="font-medium text-slate-900 truncate max-w-[200px]">
                {fileInfo?.name}
              </h4>
              <div class="flex items-center gap-2 mt-1">
                <Badge variant="secondary" class="text-xs">
                  {fileInfo?.extension}
                </Badge>
                <span class="text-xs text-slate-500">{fileInfo?.size}</span>
              </div>
            </div>
          </div>
          
          <div class="flex items-center gap-2">
            <Button variant="outline" size="sm" onclick={handlePreview}>
              <AppIcon name="eye" size={14} class="mr-1" />
              Aperçu
            </Button>
            <Button size="sm" onclick={handleDownload} disabled={isLoading}>
              {#if isLoading}
                <AppIcon name="refresh" size={14} class="mr-1 animate-spin" />
                Téléchargement...
              {:else}
                <AppIcon name="download" size={14} class="mr-1" />
                Télécharger
              {/if}
            </Button>
          </div>
        </div>
        
        {#if error}
          <div class="mt-3 p-2 bg-red-50 border border-red-200 rounded-lg">
            <p class="text-sm text-red-600">{error}</p>
          </div>
        {/if}
      </CardContent>
    </Card>

    <!-- Preview Options -->
    <Card class="border-slate-200">
      <CardContent class="p-4">
        <h4 class="font-medium text-slate-900 mb-3">Options de visualisation</h4>
        <div class="space-y-3">
          <!-- Option 1: Native PDF Viewer -->
          <div class="flex items-center justify-between p-3 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors">
            <div class="flex items-center gap-3">
              <AppIcon name="globe" size={16} class="text-slate-400" />
              <div>
                <p class="text-sm font-medium text-slate-900">Visualiseur natif</p>
                <p class="text-xs text-slate-500">Ouvre dans un nouvel onglet du navigateur</p>
              </div>
            </div>
            <Button variant="ghost" size="sm" onclick={handlePreview}>
              Ouvrir
            </Button>
          </div>

          <!-- Option 2: Download -->
          <div class="flex items-center justify-between p-3 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors">
            <div class="flex items-center gap-3">
              <AppIcon name="download" size={16} class="text-slate-400" />
              <div>
                <p class="text-sm font-medium text-slate-900">Téléchargement local</p>
                <p class="text-xs text-slate-500">Télécharge pour ouvrir avec votre lecteur PDF</p>
              </div>
            </div>
            <Button variant="ghost" size="sm" onclick={handleDownload} disabled={isLoading}>
              {#if isLoading}
                <AppIcon name="refresh" size={14} class="animate-spin" />
              {:else}
                <AppIcon name="download" size={14} />
              {/if}
            </Button>
          </div>

          <!-- Option 3: Google Docs Viewer (fallback) -->
          <div class="flex items-center justify-between p-3 border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors">
            <div class="flex items-center gap-3">
              <AppIcon name="external-link" size={16} class="text-slate-400" />
              <div>
                <p class="text-sm font-medium text-slate-900">Google Docs Viewer</p>
                <p class="text-xs text-slate-500">Visualiseur en ligne alternatif</p>
              </div>
            </div>
            <Button variant="ghost" size="sm" onclick={() => window.open(`https://docs.google.com/viewer?url=${encodeURIComponent(resumeUrl)}&embedded=true`, '_blank')}>
              Ouvrir
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>

    <!-- Tips -->
    <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
      <div class="flex items-start gap-3">
        <AppIcon name="info" size={16} class="text-blue-600 mt-0.5" />
        <div>
          <h5 class="text-sm font-medium text-blue-900 mb-1">Conseil de visualisation</h5>
          <p class="text-sm text-blue-700">
            Pour une meilleure expérience, utilisez le visualiseur natif de votre navigateur ou téléchargez le fichier pour l'ouvrir avec votre lecteur PDF habituel.
          </p>
        </div>
      </div>
    </div>
  {/if}
</div>

