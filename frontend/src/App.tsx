import { lazy, useEffect } from "react"
import { Routes, Route, useLocation } from "react-router"

const Homepage = lazy(() => (import("./pages/homepage.tsx")))
const Searchpage = lazy(() => (import("./pages/topictrendspage.tsx")))
const CategoryTrendsPage = lazy(() => (import("./pages/categorytrendspage.tsx")))
const Subredditstatisticspage = lazy(() => (import("./pages/subreddittrendspage.tsx")))
const ComparisonPage = lazy(() => (import("./pages/comparisonpage.tsx")))
const UserStatisticsPage = lazy(() => (import("./pages/userstatisticspage.tsx")))
const Bookmarkpage = lazy(() => (import("./pages/bookmarkpage.tsx")))
const Profilepage = lazy(() => (import("./pages/profilepage.tsx")))
const LoginPage = lazy(() => (import("./pages/loginpage.tsx")))

function App() {
  const location = useLocation();

  useEffect(() => {
    const subpage = location.pathname === '/' ? 'Home' : location.pathname.replace('/', '');
    document.title = `Cyphria - ${subpage.charAt(0).toUpperCase() + subpage.slice(1)}`;
  }, [location]);

  return (
    <Routes>
      <Route path="" element={<Homepage/>}/>
      <Route path="/topic" element={<Searchpage/>}/>
      <Route path="/subreddit" element={<Subredditstatisticspage />}/>
      <Route path="/category" element={<CategoryTrendsPage/>}/>
      <Route path="/comparison" element={<ComparisonPage/>}/>
      <Route path="/user" element={<UserStatisticsPage/>}/>
      <Route path="/bookmarks" element={<Bookmarkpage/>}/>
      <Route path="/profile" element={<Profilepage/>}/>
      <Route path="/login" element={<LoginPage/>} />
    </Routes>
  )
}

export default App
