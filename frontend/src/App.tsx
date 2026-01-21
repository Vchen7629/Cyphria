import { lazy, useEffect } from "react"
import { Routes, Route, useLocation } from "react-router"

const Homepage = lazy(() => (import("./pages/HomePage.tsx")))
const CategoryPage = lazy(() => (import("./pages/CategoryPage.tsx")))
const TopicPage = lazy(() => (import("./pages/TopicPage.tsx")))

function App() {
  const location = useLocation();

  useEffect(() => {
    const subpage = location.pathname === '/' ? 'Home' : location.pathname.replace('/', '');
    document.title = `Cyphria - ${subpage.charAt(0).toUpperCase() + subpage.slice(1)}`;
  }, [location]);

  return (
    <Routes>
      <Route path="" element={<Homepage />} />
      <Route path="/:category" element={<CategoryPage />} />
      <Route path="/:category/:topic" element={<TopicPage />} />
    </Routes>
  )
}

export default App
