import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

const authApiQuery = fetchBaseQuery({
    //baseUrl: 'http://localhost:3000',
    baseUrl: 'https://cyphria.com/loginapi',
    credentials: 'include',
})

export const authSlice = createApi({
    reducerPath: 'authApi',
    baseQuery: authApiQuery,
    endpoints: () => ({}),
    tagTypes: ["User"]
})