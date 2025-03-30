import { baseSlice } from "../base/baseSlice";

export const queryApiSlice = baseSlice.injectEndpoints({
    endpoints: builder => ({
        topic: builder.mutation({
            query: (topic) => ({
                url: "/trends/topic",
                method: "POST",
            }),
        }),
        category: builder.mutation({
            query: (category) => ({
                url: "/trends/category",
                method: "POST",
            })
        }),
        subreddit: builder.mutation({
            query: (subreddit) => ({
                url: "/trends/subreddit",
                method: "POST",
            })
        }),
        comparison: builder.mutation({
            query: (body) => ({
                url: "/trends/comparison",
                method: "POST",
            })
        })
    })
})

export const {
    useTopicMutation,
    useCategoryMutation,
    useSubredditMutation,
    useComparisonMutation,
} = queryApiSlice