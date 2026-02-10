import { 
  GET, 
  POST, 
  DELETE, 
  PUT, 
  PATCH, 
  UPLOAD 
} from "./http";


class APIEndPoint {
  collection_endpoint: string
  item_endpoint: string
  origin?: string

  constructor(endpoint: string, item_endpoint: string, origin?: string) {
    this.collection_endpoint = endpoint;
    this.item_endpoint = item_endpoint;
    this.origin = origin;
  }


  /**
   * Make a GET request to the collection endpoint.
   *
   * @param args - An object of query parameters to pass to the GET request.
   * @returns A promise that resolves to the response of the GET request, which will have a `results` property with the list of items.
   */
  async list(...args: any[]): Promise<any> {
    return await GET(this.collection_endpoint, this.origin)(...args);
  }


  async create(...args: any[]) {
    return await POST(this.collection_endpoint, this.origin)(...args);
  }

  async upload(args: any[], form: FormData, setProgressState: (progress: number) => void) {
    const tokens = this.collection_endpoint.split('/');
    const mappedUrl = tokens.map((token, i) => token.startsWith(':') ? args.shift() : token).join('/');
    return UPLOAD(mappedUrl, form, setProgressState);
  }

  async retrieve(...args: any[]) {
    return await GET(this.item_endpoint, this.origin)(...args);
  }

  async update(...args: any[]) {
    return await PUT(this.item_endpoint, this.origin)(...args);
  }

  async destroy(...args: any[]) {
    return await DELETE(this.item_endpoint, this.origin)(...args);
  }

  async partial_update(...args: any[]) {
    return await PATCH(this.item_endpoint, this.origin)(...args);
  }
}


export default APIEndPoint;

