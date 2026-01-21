import MainLayout from "../components/layout/MainLayout";
import { mockTopics } from "../mock/mockData";
import TrendingTopicsList from "../components/home/TrendingTopicsList";
import BrowseCateroriesGrid from "../components/home/BrowseCategoriesGrid";

/**
 @component

 @description - Homepage component that displays on / route. 
 */
const HomePage = () => {
  return (
    <MainLayout>
      <div className="max-w-4xl mx-auto px-6 py-8">
        <div className="flex flex-col items-center mb-8">
          <h1 className="text-2xl font-semibold text-zinc-100 mb-2">
            Product Rankings
          </h1>
          <p className="text-sm text-zinc-500">
            Crowd-sourced product ratings from Reddit discussions
          </p>
        </div>

        <div className="space-y-10 h-fit">
          <section>
            <h2 className="text-lg font-medium text-zinc-100">Browse Categories</h2>
            <BrowseCateroriesGrid />
          </section>
          <TrendingTopicsList topics={mockTopics} />
        </div>
      </div>
    </MainLayout>
  );
}

export default HomePage