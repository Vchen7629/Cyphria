import { authSlice } from "../base/authSlice";
import { logOut } from "../state/authstate";

export const authApiSlice = authSlice.injectEndpoints({
    endpoints: builder => ({
        login: builder.mutation({
            query: credentials => ({
                url: "/login",
                method: "POST",
                body: { ...credentials},   
                credentials: 'include', 
            }),
        }),
        Logout: builder.mutation({
            query: (credentials) => ({
                url: "/logout",
                method: "POST",
                body: {...credentials}
            }),
            async onQueryStarted(_, { dispatch, queryFulfilled }) {
                await queryFulfilled; 
                dispatch(logOut());
            }
        })
    })
})

export const {
    useLoginMutation,
    useLogoutMutation
} = authApiSlice