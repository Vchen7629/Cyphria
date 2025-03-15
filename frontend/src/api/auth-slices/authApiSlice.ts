import { baseSlice } from "../base/baseSlice";

export const authApiSlice = baseSlice.injectEndpoints({
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
            query: () => ({
                url: "/logout",
                method: "POST",
                credentials: 'include',
            })
        })
    })
})

export const {
    useLoginMutation,
    useLogoutMutation
} = authApiSlice