import axios from "axios";

/**
 * Example of API response when user needs to verify email:
 * {
    "status": 401,
    "data": {
        "flows": [
            {
                "id": "login"
            },
            {
                "id": "verify_email",
                "is_pending": true
            }
        ]
    },
    "meta": {
        "is_authenticated": false
    }
}
 */

/**
 * Checks if an error response indicates that the user must verify their email
 * @param err The error object from an API request
 * @returns boolean True if the error indicates email verification is required
 */
export function is_must_verify_email_error(err: any): boolean {
  if (!err) 
    return false;

  if (err.status !== 401) 
    return false;
    
  const data = err.data;
  if (!data || !data.flows || !Array.isArray(data.flows)) return false;
    
  return data.flows.some((flow: any) => 
    flow.id === 'verify_email' && flow.is_pending === true
  );
}

export function is_axios_error(error: any){
  return axios.isAxiosError(error);
}

export function is_call_to_login(err: any){
  if (!err) 
    return false;

  if (err.status !== 401) 
    return false;
    
  const data = err.data;
  if (!data || !data.flows || !Array.isArray(data.flows)) 
    return false;
    
  return data.flows[0].id === 'login';
}

export function isPromise(value: any): value is Promise<any> {
  return value !== null && value !== undefined && typeof value.then === 'function';
}


export function is_nan(value: string){
  const val = parseInt(value)
  return Number.isNaN(val);
}

export function format_currency(currency: any, value: string, show_null = false){
  if (!show_null && is_nan(value)) 
    return '';
  return currency(value).format();
}


export function to_deep_string(val: any): string[] {
  if (Array.isArray(val)) {
    return val.map((v) => String(v));
  } else if (val && typeof val === 'object') {
    return Object.entries(val).map(
      (k, val) => `${k}: ${val}`
    );
  } else {
    return [String(val)];
  }
}

