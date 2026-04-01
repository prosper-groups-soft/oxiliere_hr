import { get_api_auth_origin } from '@/utilities/http/urls';
import APIEndPoint from '@/utilities/http/rest';


export const AuthEndpoint = {
	login: new APIEndPoint('/auth/login', '/auth/login', get_api_auth_origin()),
	reauthenticate: new APIEndPoint(
		'/auth/reauthenticate',
		'/auth/reauthenticate',
		get_api_auth_origin()
	),
	logout: new APIEndPoint('/auth/logout', '/auth/logout', get_api_auth_origin()),
	refresh_token: new APIEndPoint('/auth/refresh', '/auth/refresh', get_api_auth_origin())
};


export const MFAEndpoint = {
	verify: new APIEndPoint('/auth/mfa/verify', '/auth/mfa/verify', get_api_auth_origin()),
	reauthenticate: new APIEndPoint(
		'/auth/mfa/reauthenticate',
		'/auth/mfa/reauthenticate',
		get_api_auth_origin()
	)
};


export const UserAccountEndpoints = {
	users: new APIEndPoint('/users/:user_id', '/users/:user_id', get_api_auth_origin()),
	session: new APIEndPoint('/users/session', '/users/session', get_api_auth_origin()),
	privacy: new APIEndPoint(
		'/users/:user_id/privacy',
		'/users/:user_id/privacy',
		get_api_auth_origin()
	),
	billing: new APIEndPoint(
		'/users/:user_id/billing',
		'/users/:user_id/billing',
		get_api_auth_origin()
	),
	accounts: new APIEndPoint('/users-accounts', '/users-accounts', get_api_auth_origin()),
	account_activate: new APIEndPoint(
		'/users-accounts/:user_