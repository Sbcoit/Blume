import { createClient, SupabaseClient } from "@supabase/supabase-js";

let supabase: SupabaseClient | null = null;

export function getSupabaseClient(): SupabaseClient {
  if (!supabase) {
    const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
    const anonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;

    if (!url || !anonKey) {
      // During scaffold, warn loudly so env can be wired later.
      console.warn(
        "[Supabase] NEXT_PUBLIC_SUPABASE_URL or NEXT_PUBLIC_SUPABASE_ANON_KEY is not set. Using placeholder values."
      );
    }

    supabase = createClient(
      url || "https://placeholder.supabase.co",
      anonKey || "public-anon-key"
    );
  }

  return supabase;
}


