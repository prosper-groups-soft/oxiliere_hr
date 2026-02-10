import { goto } from "$app/navigation";
import { current_user_store, user_logging_out } from "$lib/stores/auth";
import { AuthEndpoint } from "@/api/endpoints/auth";
import BaseEndpoints from "@/api/endpoints";
import { UserAccountEndpoints } from "@/api/endpoints/auth";
import axios from "axios";
import { toast } from "svelte-sonner";
import { removeAuthCookie, setAuthCookie } from "../auth/auth-cookies";
import { get_logout_redirect_url } from "../http/urls";


export async function load_user(force = false) {
  let cu: any | null = null;

  current_user_store.subscribe((value) => {
    cu = value;
  })();

  if (!cu || force) {
    try {
      const data = await UserAccountEndpoints.session.retrieve();
      current_user_store.set(data);
      setAuthCookie();
    } catch (e: any) {
      if (axios.isAxiosError(e) && e.response?.status === 401) {
        // clean_user_auth();
        return;
      }
    }
  }
}


export function clean_user_auth() {
  current_user_store.set(null);
  user_logging_out.set(false);
  removeAuthCookie();
}


export async function logout() {
  const logout_redirect = get_logout_redirect_url();
  try {
    user_logging_out.set(true);
    await AuthEndpoint.logout.create();
    clean_user_auth();
    goto(logout_redirect);
  } catch (e) {
    if (axios.isAxiosError(e) && e.response?.status === 401) {
      clean_user_auth();
      // disconnect();
      goto(logout_redirect);
    } else {
      toast.error("Erreur de déconnexion", {
        description: "Une erreur est survenue lors de la déconnexion",
      });
    }
  }
}


export async function init_csrf() {
  try {
    await BaseEndpoints.init_csrf.retrieve();
  } catch (error) {
    // pass
  }
}

