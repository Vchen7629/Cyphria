import { authSlice } from "../base/authSlice";
import { setCredentials } from "../state/authstate";

export const authApiSlice = authSlice.injectEndpoints({
    endpoints: builder => ({
        getUserData: builder.query< any, void>({
            query: () => ({
                url: "/getuserdata",
                method: "POST",
                credentials: "include"
            }),
            providesTags: ['User'],
            async onQueryStarted(_, { dispatch, queryFulfilled }) {
                try {
                    const { data } = await queryFulfilled
                    const { username, uuid } = data
                    dispatch(setCredentials({ uuid, username }))
                } catch (err) {
                    console.error('Login Error', err)
                }
            }
        })
    })
})

export const {
    useGetUserDataQuery
} = authApiSlice