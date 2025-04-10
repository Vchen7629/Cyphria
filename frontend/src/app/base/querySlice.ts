import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

const queryApiQuery = fetchBaseQuery({
    baseUrl: 'http://127.0.0.1:5000',
    credentials: 'include',
})

export const querySlice = createApi({
    reducerPath: 'queryApi',
    baseQuery: queryApiQuery,
    endpoints: () => ({})
})