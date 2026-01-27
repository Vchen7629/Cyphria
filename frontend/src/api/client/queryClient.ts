import { QueryClient } from "@tanstack/react-query"

export const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            staleTime: 5 * 60 * 1000,
            gcTime: 30 * 60 * 1000, // keep cache in memory for 30 mins, clean up after
            refetchOnWindowFocus: false // Don't refetch when user returns to tab
        }
    }
})