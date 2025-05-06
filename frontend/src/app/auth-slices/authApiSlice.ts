import { authSlice } from "../base/authSlice";
import { logOut } from "../state/authstate";

export const authApiSlice = authSlice.injectEndpoints({
    endpoints: builder => ({
        login: builder.mutation<any, { username: string, password: string }>({
            query: credentials => ({
                url: "/login",
                method: "POST",
                body: { ...credentials},   
                credentials: 'include', 
            }),
            invalidatesTags: ['User'], 
        }),
        Logout: builder.mutation({
            query: (credentials) => ({
                url: "/logout",
                method: "POST",
                body: {...credentials}
            }),
            async onQueryStarted(_, { dispatch, queryFulfilled }) {
                await queryFulfilled; 
                sessionStorage.clear();
                dispatch(logOut());
            }
        })
    })
})

export const {
    useLoginMutation,
    useLogoutMutation
} = authApiSlice