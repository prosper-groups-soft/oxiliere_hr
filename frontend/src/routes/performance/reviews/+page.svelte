<script lang="ts">
  import { page } from '$app/state';
  import { QueryClient, keepPreviousData, useQuery } from '@tanstack/svelte-query';
  import { performanceEndpoint } from '@/features/performance/api/performance.endpoints';
  import type { PerformanceReviewBackendResponse, ReviewStatus } from '@/features/performance/types/types';
  import { REVIEW_STATUS_LABELS, REVIEW_STATUS_COLORS } from '@/features/performance/constants';

  // Simple view for now — will extract to components later
  let search = $state('');
  let statusFilter = $state<ReviewStatus | ''>('');
  let pageNum = $state(1);

  // Demo employee ID — will come from auth context
  let employeeId = $state('');

  const queryClient = new QueryClient();

  const reviewsQuery = useQuery<{ items: PerformanceReviewBackendResponse[]; count: number }>(() => ({
    queryKey: ['performance-reviews', employeeId, pageNum, search, statusFilter],
    queryFn: () => performanceEndpoint.listEmployeeReviews(employeeId, {
      page: pageNum,
      search: search || undefined,
      status: statusFilter || undefined,
    }),
    placeholderData: keepPreviousData,
    enabled: !!employeeId,
  }));
</script>

<div class="space-y-6 p-6">
  <!-- Header -->
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-2xl font-bold text-slate-900">Mes Évaluations</h1>
      <p class="mt-1 text-sm text-slate-500">
        Consultez et gérez vos évaluations de performance
      </p>
    </div>
  </div>

  <!-- Filters -->
  <div class="flex items-center gap-4">
    <div class="relative flex-1 max-w-md">
      <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
        <svg class="size-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
      </div>
      <input
        type="text"
        placeholder="Rechercher..."
        bind:value={search}
        class="w-full rounded-lg border border-slate-200 bg-white py-2 pl-10 pr-3 text-sm placeholder-slate-400 focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
      />
    </div>
    <select
      bind:value={statusFilter}
      class="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
    >
      <option value="">Tous les statuts</option>
      {#each Object.entries(REVIEW_STATUS_LABELS) as [value, label]}
        <option value={value}>{label}</option>
      {/each}
    </select>
  </div>

  <!-- Reviews List -->
  {#if reviewsQuery.isLoading}
    <div class="flex justify-center py-12">
      <div class="size-8 animate-spin rounded-full border-4 border-slate-200 border-t-blue-600" />
    </div>
  {:else if reviewsQuery.data?.items.length}
    <div class="space-y-3">
      {#each reviewsQuery.data.items as review (review.id)}
        <div class="rounded-xl border border-slate-200 bg-white p-5 transition-all hover:shadow-md hover:border-slate-300">
          <div class="flex items-start justify-between">
            <div class="space-y-1">
              <div class="text-sm text-slate-500">
                {review.review_period_label}
              </div>
              <div class="text-lg font-semibold text-slate-900">
                {review.employee_name}
              </div>
              {#if review.reviewer_name}
                <div class="text-sm text-slate-500">
                  Évaluateur : {review.reviewer_name}
                </div>
              {/if}
            </div>
            <span
              class="inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium {REVIEW_STATUS_COLORS[review.status].bg} {REVIEW_STATUS_COLORS[review.status].text}"
            >
              <span class="size-1.5 rounded-full {REVIEW_STATUS_COLORS[review.status].dot}" />
              {REVIEW_STATUS_LABELS[review.status]}
            </span>
          </div>
          {#if review.overall_rating}
            <div class="mt-3 flex items-center gap-1">
              <span class="text-sm text-slate-500">Note globale :</span>
              <div class="flex items-center gap-0.5">
                {#each Array(5) as _, i}
                  <svg
                    class="size-4 {i < (review.overall_rating ?? 0) ? 'text-amber-400' : 'text-slate-200'}"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                {/each}
              </div>
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {:else}
    <div class="rounded-xl border-2 border-dashed border-slate-200 py-16 text-center">
      <svg class="mx-auto size-12 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
      </svg>
      <h3 class="mt-4 text-sm font-medium text-slate-900">Aucune évaluation</h3>
      <p class="mt-1 text-sm text-slate-500">
        Aucune évaluation trouvée pour cet employé.
      </p>
    </div>
  {/if}
</div>
