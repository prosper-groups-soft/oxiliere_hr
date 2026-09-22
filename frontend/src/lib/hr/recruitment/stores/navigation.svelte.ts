/**
 * Navigation store for recruitment module
 * Maintains navigation state between pages
 */
export const recruitmentNavigationStore = $state({
	/**
	 * Active tab in recruitment section
	 */
	activeTab: 'candidates' as 'candidates' | 'pipeline',

	/**
	 * Last visited page before navigating to details
	 */
	lastVisitedTab: 'candidates' as 'candidates' | 'pipeline',

	/**
	 * Updates the active tab
	 */
	setActiveTab(tab: 'candidates' | 'pipeline') {
		this.activeTab = tab;
		this.lastVisitedTab = tab;
	},

	/**
	 * Resets navigation state
	 */
	reset() {
		this.activeTab = 'candidates';
		this.lastVisitedTab = 'candidates';
	}
});
