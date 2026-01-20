import MainLayout from "../components/layout/MainLayout";
import CategoryGrid from "../components/home/CategoryGrid";
import { mockCategories, mockTopics } from "../mock/mockData";
import TrendingTopics from "../components/home/TrendingTopics"

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
          <CategoryGrid categories={mockCategories} />
          <TrendingTopics topics={mockTopics} />
        </div>
      </div>
    </MainLayout>
  );
}

export default HomePage