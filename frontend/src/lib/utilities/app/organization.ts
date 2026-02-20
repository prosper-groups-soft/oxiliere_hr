import { 
  ORGANIZATION_TYPES, 
  ORGANIZATION_SIZES, 
  ORGANIZATION_VISIBILITY, 
  ORGANIZATION_INDUSTRIES, 
  SUBSCRIPTION_PLANS 
} from '@/constants/app/base';


export const getOrganizationTypeLabel = (type: string) => {
	return ORGANIZATION_TYPES[type as keyof typeof ORGANIZATION_TYPES] || type;
};


export const getOrganizationSizeLabel = (size: string) => {
	return ORGANIZATION_SIZES[size as keyof typeof ORGANIZATION_SIZES] || size;
};


export const getVisibilityLabel = (visibility: string) => {
	return ORGANIZATION_VISIBILITY[visibility as keyof typeof ORGANIZATION_VISIBILITY] || visibility;
};


export const getIndustryLabel = (industry: string) => {
	return ORGANIZATION_INDUSTRIES[industry as keyof typeof ORGANIZATION_INDUSTRIES] || industry;
};


export const getSubscriptionLabel = (plan: string) => {
	return SUBSCRIPTION_PLANS[plan as keyof typeof SUBSCRIPTION_PLANS] || "Gratuit";
};

