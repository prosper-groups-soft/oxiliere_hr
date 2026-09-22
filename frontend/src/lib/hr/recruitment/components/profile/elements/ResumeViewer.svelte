<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Badge } from "@/components/ui/badge";
  import { Button } from "@/components/ui/button";
  import { Card, CardContent } from "@/components/ui/card";
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import { getMediaUrl } from "@/utilities/common/media";


  let { resumeUrl } = $props<{ resumeUrl?: string }>();

  // Resolve the full media URL
  const resolvedResumeUrl = $derived(resumeUrl ? getMediaUrl(resumeUrl) : null);

  let isLoading = $state(false);
  let error = $state<string | null>(null);

  // Handle file download
  async function handleDownload() {
    if (!resolvedResumeUrl) return;
    
    isLoading = true;
    error = null;
    
    try {
      // Create download link
      const link = document.createElement('a');
      link.href = resolvedResumeUrl;
      link.download = resolvedResumeUrl.split('/').pop() || 'resume.pdf';
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
    if (!resolvedResumeUrl) return;
    
    window.open(resolvedResumeUrl, '_blank');
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
    };
  }

  const fileInfo = $derived(getFileInfo());

  // Fetch real file size via HEAD request
  let fileSize = $state<string | null>(null);
  $effect(() => {
    if (!resolvedResumeUrl) return;
    
    fetch(resolvedResumeUrl, { method: 'HEAD' })
      .then(res => {
        const length = res.headers.get('Content-Length');
        if (length) {
          const bytes = parseInt(length, 10);
          if (bytes < 1024) {
            fileSize = `${bytes} o`;
          } else if (bytes < 1024 * 1024) {
            fileSize = `${(bytes / 1024).toFixed(1)} Ko`;
          } else {
            fileSize = `${(bytes / (1024 * 1024)).toFixed(1)} Mo`;
          }
        }
      })
      .catch(() => { /* ignore */ });
  });
</script>


<div class="">
  {#if !resumeUrl}
    <div class="text-center py-8 border-2 border-dashed border-slate-300 rounded-lg">
      <AppIcon name="file" size={34} class="text-slate-300 mx-auto mb-3" strokeWidth={1.2} />
      <p class="text-slate-500 mb-1 text-[0.9rem]">Aucun CV disponible</p>
      <p class="text-sm text-slate-400 text-[0.83rem]">Le CV n'a pas été uploadé pour ce candidat</p>
    </div>
  {:else}
    <!-- File Info Card -->
    <Card class="border border-slate-200 shadow-none py-1.5!">
      <CardContent class="p-3 py-1!">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="h-12 w-12 bg-red-50 border border-red-200 rounded-lg flex items-center justify-center">
              <AppIcon name="file" size={20} class="text-red-600" />
            </div>
            <div>
              <h4 class="font-medium text-slate-900 truncate max-w-[200px] text-sm">
                {fileInfo?.name}
              </h4>
              <div class="flex items-center gap-2 mt-1">
                <Badge variant="secondary" class="text-xs">
                  {fileInfo?.extension || 'FICHIER'}
                </Badge>
                {#if fileSize}
                  <span class="text-xs text-slate-500">{fileSize}</span>
                {/if}
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
            <p class="text-sm text-red-600">
              <AppIcon name="circle-x" size={16} class="text-red-700"/>
              {error}
            </p>
          </div>
        {/if}
      </CardContent>
    </Card>

    <!-- Quick Actions -->
    <div class="flexx hidden items-center gap-2 p-3 bg-slate-50/50 rounded-xl border border-slate-100">
      <span class="text-[0.84rem] font-medium text-slate-500 uppercase tracking-wider mr-1">Actions</span>
      <Button variant="outline" size="sm" onclick={handlePreview} class="h-7 text-[0.75rem] rounded-lg gap-1.5">
        <AppIcon name="eye" size={13} /> Ouvrir
      </Button>
      <Button variant="outline" size="sm" onclick={handleDownload} disabled={isLoading} class="h-7 text-[0.84rem] rounded-lg gap-1.5">
        {#if isLoading}
          <AnimateSpin text="" class="size-3 border-white" />
        {:else}
          <AppIcon name="download" size={13} />
        {/if}
        Télécharger
      </Button>
      <Button variant="outline" size="sm" onclick={() => window.open(`https://docs.google.com/viewer?url=${encodeURIComponent(resolvedResumeUrl ?? '')}&embedded=true`, '_blank')} class="h-7 text-[0.84rem] rounded-lg gap-1.5">
        <AppIcon name="external-link" size={13} /> Google Viewer
      </Button>
    </div>
  {/if}
</div>

