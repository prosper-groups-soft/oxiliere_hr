import APIEndPoint from '@/utilities/http/rest';


const AccessEndpoints = {
	scopes: new APIEndPoint('/api/access/scopes', '/api/access/scopes'),
	roles: new APIEndPoint('/api/access/roles', '/api/access/roles'),
	groups: new APIEndPoint('/api/access/groups', '/api/access/groups/:slug'),
	roleGrants: new APIEndPoint('/api/access/role-grants', '/api/access/role-grants'),
	grants: new APIEndPoint('/api/access/grants', '/api/access/grants'),
	
	// Complex endpoints
	syncGroup: (slug: string) => new APIEndPoint(`/api/access/groups/${slug}/sync`, `/api/access/groups/${slug}/sync`),
	assignGroup: new APIEndPoint('/api/access/users/assign-group', '/api/access/users/assign-group'),
	revokeGroup: new APIEndPoint('/api/access/users/revoke-group', '/api/access/users/revoke-group'),
  assignRole: new APIEndPoint('/api/access/users/assign-role', '/api/access/users/assign-role')
};


export default AccessEndpoints;

