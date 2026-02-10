import APIEndPoint from "@/utilities/http/rest";


const OrganizationEndpoints = {
  organizations: new APIEndPoint(
    '/organizations',
    '/organizations/:org_id'
  ),
  organization_users: new APIEndPoint(
    '/organizations/:org_id/users',
    '/organizations/:org_id/users/:user_id'
  ),
  check_company_id: new APIEndPoint(
    '/organizations/check_id/:slug',
    '/organizations/check_id/:slug'
  ),
};


export default OrganizationEndpoints;

