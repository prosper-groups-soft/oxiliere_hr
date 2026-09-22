import APIEndPoint from '@/hr/utilities/http/rest';


const UserEndpoints = {
	users: new APIEndPoint('/api/users', '/api/users/:id'),
};


export default UserEndpoints;

