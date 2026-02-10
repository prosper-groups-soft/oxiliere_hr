import APIEndPoint from '@/utilities/http/rest';


export const MonEndpoint = {
  items: new APIEndPoint('/items', '/items/:id'),
};

