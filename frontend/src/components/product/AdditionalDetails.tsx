import type { Sentiment, Comment } from "../../mock/types";
import SentimentBar from "./SentimentBar";
import TopComments from "./TopComments";

interface ProductDetailsProps {
  sentiment: Sentiment;
  comments: Comment[];
  isExpanded: boolean;
}

/**
 @component 

 @description - displays additional details about the product such as the sentiment breakdown, top reddit comments

 @param {Sentiment} sentiment - The Sentiment Counts: positive, neutral, negative comments mentioning this product
 @param {Comment[]} comments - List of top 5 reddit comments mentioning this product
 @param {boolean} isExpanded - boolean that handles whether to display this component or not

 @returns {} - Returns the component
 */
const ProductAdditionalDetails = ({ sentiment, comments, isExpanded }: ProductDetailsProps) => {
  if (!isExpanded) return null;

  return (
    <div className="px-4 pb-4 pt-2 space-y-4 border-t border-zinc-800/40 mt-3 ml-12">
      <SentimentBar sentiment={sentiment} />
      <TopComments comments={comments} />
    </div>
  );
}

export default ProductAdditionalDetails
