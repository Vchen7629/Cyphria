import { lazy, useEffect } from "react"
import { Routes, Route, useLocation } from "react-router"

const Homepage = lazy(() => (import("./features/homepage/pages/homepage.tsx")))
const SearchPage = lazy(() => (import("./features/topic/pages/topic-trends.tsx")))
const CategoryTrendsPage = lazy(() => (import("./features/category/pages/categorytrendspage.tsx")))
const SubredditStatisticsPage = lazy(() => (import("./features/subreddit/pages/subreddittrendspage.tsx")))
const ComparisonPage = lazy(() => (import("./features/topic/pages/comparison.tsx")))

function App() {
  const location = useLocation();

  useEffect(() => {
    const subpage = location.pathname === '/' ? 'Home' : location.pathname.replace('/', '');
    document.title = `Cyphria - ${subpage.charAt(0).toUpperCase() + subpage.slice(1)}`;
  }, [location]);

  return (
    <Routes>
      <Route path="" element={<Homepage/>}/>
      <Route path="/topic" element={<SearchPage/>}/>
      <Route path="/subreddit" element={<SubredditStatisticsPage />}/>
      <Route path="/category" element={<CategoryTrendsPage/>}/>
      <Route path="/comparison" element={<ComparisonPage/>}/>
    </Routes>
  )
}

export default App
