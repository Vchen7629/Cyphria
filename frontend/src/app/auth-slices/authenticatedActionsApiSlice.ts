import { authSlice } from "../base/authSlice";
import { setCredentials } from "../state/authstate";

export const authApiSlice = authSlice.injectEndpoints({
    endpoints: builder => ({
        getUserData: builder.mutation< any, void>({
            query: () => ({
                url: "/getuserdata",
                method: "POST",
                credentials: "include"
            }),
            async onQueryStarted(_, { dispatch, queryFulfilled }) {
                try {
                    const { data } = await queryFulfilled
                    const { username, uuid } = data
                    const result = dispatch(setCredentials({ uuid, username }))
                    console.log(result)
                } catch (err) {
                    console.error('Login Error', err)
                }
            }
        })
    })
})

export const {
    useGetUserDataMutation
} = authApiSlice