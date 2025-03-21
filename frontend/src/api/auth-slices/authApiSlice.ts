import { baseSlice } from "../base/baseSlice";
import { logOut, setCredentials } from "../state/authstate";

export const authApiSlice = baseSlice.injectEndpoints({
    endpoints: builder => ({
        login: builder.mutation({
            query: credentials => ({
                url: "/login",
                method: "POST",
                body: { ...credentials},   
                credentials: 'include', 
            }),
            async onQueryStarted(_, { dispatch, queryFulfilled }) {
                try {
                    const { data } = await queryFulfilled
                    const { uuid, username } = data.user
                    const result = dispatch(setCredentials({ uuid, username }))
                    console.log(result)
                } catch (err) {
                    console.error('Login Error', err)
                }
            }
        }),
        Logout: builder.mutation({
            query: () => ({
                url: "/logout",
                method: "POST",
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