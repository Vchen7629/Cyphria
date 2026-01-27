import { useQuery } from '@tanstack/react-query';
import { ProductTopicService } from '../../api/services/product_topic';

interface TotalOpinionsProps {
    product_topic: string
    time_window: string
}

/**
 @hook

 @description - hook called when the user views the topic page, fetches and displays
 the total number of opinions count for the topic and time window

 @param product_topic - the product topic we are fetching total opinions count for
 @param time_window - the product window we are fetching total opinions count for

 @returns - the total products opinion count for that topic and time window
 */
export function useGetTotalOpnions({ product_topic, time_window }: TotalOpinionsProps) {
    return useQuery<number>({
        queryKey: ['topic_total_opinions', product_topic],
        queryFn: async () => {
            return await ProductTopicService.total_opinions({ product_topic, time_window });
        },
        staleTime: 1 * 60 * 1000, // Cache for 1 minute
    });
}