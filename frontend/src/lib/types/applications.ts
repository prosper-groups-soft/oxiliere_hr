export type ApplicationStatus = 'running' | 'success' | 'not_installed' | 'stopped' | 'failed' | 'canceled';


// User Application Types
export interface UserApplication {
    id: string;
    user_id: string;
    application_id: string;
    application_name: string;
    application_description: string;
    application_icon: any;
    application_codename: string;
    is_favorite: boolean;
    installed_at: string;
    last_accessed: string;
    access_count: number;
    status: 'active' | 'inactive' | 'suspended';
    version: string;
}

export interface UserApplicationSummary {
    total_applications: number;
    favorite_applications: number;
    recently_accessed: number;
    total_access_count: number;
}

export interface UserApplicationInstall {
    application_id: string;
    configuration?: Record<string, any>;
}

export interface UserApplicationActivity {
    date: string;
    application_name: string;
    action: string;
    count: number;
}

// Organization Application Types
export interface Application {
    id: string;
    name: string;
    codename: string;
    description: string;
    version: string;
    logo: string;
    url: string;
    installed_app?: InstalledApplication;
    category: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
}

export interface ApplicationFeature {
    id: string;
    application_id: string;
    title: string;
    description: string;
    created_at: string;
    updated_at: string;
}

export interface InstalledApplication {
    id: string;
    application: {
        id: string;
        name: string;
        description: string;
        version: string;
        logo: string;
        url: string;
        category: string;
        is_premium: boolean;
        is_active: boolean;
        target: string;
        created_at: string;
        updated_at: string;
    };
    is_active: boolean;
    status: ApplicationStatus;
    default_access_policy: string;
    created_at: string;
    updated_at: string;
}

export interface ApplicationInstall {
    application_id: string;
    organisation_id?: string;
}

export interface ApplicationUninstall {
    application_id: string;
    organisation_id?: string;
    keep_data?: boolean;
    reason?: string;
}
