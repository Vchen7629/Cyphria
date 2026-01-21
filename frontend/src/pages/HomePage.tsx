import MainLayout from "../components/layout/MainLayout";
import { mockCategories, mockTopics } from "../mock/mockData";
import TrendingTopics from "../components/home/TrendingTopics"
import CategoryCardDropdownButton from "../components/home/CategoryCardDropdownButton";

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
            <span className="text-sm font-light text-zinc-400"></span>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mt-6">
              {mockCategories.slice(0,6).map((category) => (
                <CategoryCardDropdownButton key={category.id} category={category} />
              ))}
            </div>
          </section>
          <TrendingTopics topics={mockTopics} />
        </div>
      </div>
    </MainLayout>
  );
}

export default HomePage