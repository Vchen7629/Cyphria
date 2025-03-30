import { querySlice } from "../base/querySlice";

export const queryApiSlice = querySlice.injectEndpoints({
    endpoints: builder => ({
        topic: builder.mutation({
            query: (topic) => ({
                url: "/trends/topic",
                method: "POST",
                body: topic
            }),
        }),
        category: builder.mutation({
            query: (category) => ({
                url: "/trends/category",
                method: "POST",
                body: category
            })
        }),
        subreddit: builder.mutation({
            query: (subreddit) => ({
                url: "/trends/subreddit",
                method: "POST",
                body: subreddit
            })
        }),
        comparison: builder.mutation({
            query: (body) => ({
                url: "/trends/comparison",
                method: "POST",
                body: body
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