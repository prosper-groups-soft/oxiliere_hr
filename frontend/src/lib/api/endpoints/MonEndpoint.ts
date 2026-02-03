// src/lib/api/endpoints/mon-endpoint.ts
import APIEndPoint from '@/utilities/rest';


export const MonEndpoint = {
  items: new APIEndPoint('/items', '/items/:id'),
};

