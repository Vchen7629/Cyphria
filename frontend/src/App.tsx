import { lazy, useEffect } from "react"
import { Routes, Route, useLocation } from "react-router"

const Homepage = lazy(() => (import("./dashboardpages/homepage.tsx")))
const FeaturesPage = lazy(() => (import("./homesubpages/featurespage.tsx")))
const ContactPage = lazy(() => (import("./homesubpages/contactpage.tsx")))
const SearchPage = lazy(() => (import("./dashboardpages/topictrendspage.tsx")))
const CategoryTrendsPage = lazy(() => (import("./dashboardpages/categorytrendspage.tsx")))
const SubredditStatisticsPage = lazy(() => (import("./dashboardpages/subreddittrendspage.tsx")))
const ComparisonPage = lazy(() => (import("./dashboardpages/comparisonpage.tsx")))
const UserStatisticsPage = lazy(() => (import("./dashboardpages/userstatisticspage.tsx")))
const BookmarkPage = lazy(() => (import("./dashboardpages/bookmarkpage.tsx")))
const ProfilePage = lazy(() => (import("./dashboardpages/profilepage.tsx")))
const LoginPage = lazy(() => (import("./dashboardpages/loginpage.tsx")))

function App() {
  const location = useLocation();

  useEffect(() => {
    const subpage = location.pathname === '/' ? 'Home' : location.pathname.replace('/', '');
    document.title = `Cyphria - ${subpage.charAt(0).toUpperCase() + subpage.slice(1)}`;
  }, [location]);

  return (
    <Routes>
      <Route path="" element={<Homepage/>}/>
      <Route path="features" element={<FeaturesPage/>}/>
      <Route path="contact" element={<ContactPage/>}/>
      <Route path="/topic" element={<SearchPage/>}/>
      <Route path="/subreddit" element={<SubredditStatisticsPage />}/>
      <Route path="/category" element={<CategoryTrendsPage/>}/>
      <Route path="/comparison" element={<ComparisonPage/>}/>
      <Route path="/user" element={<UserStatisticsPage/>}/>
      <Route path="/bookmarks" element={<BookmarkPage/>}/>
      <Route path="/profile" element={<ProfilePage/>}/>
      <Route path="/login" element={<LoginPage/>} />
    </Routes>
  )
}

export default App
