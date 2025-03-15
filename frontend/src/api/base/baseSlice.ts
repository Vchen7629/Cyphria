import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'
const baseQuery = fetchBaseQuery({
    baseUrl: 'http://localhost:3000',
})

export const baseSlice = createApi({
    baseQuery: baseQuery,
    endpoints: () => ({})
})