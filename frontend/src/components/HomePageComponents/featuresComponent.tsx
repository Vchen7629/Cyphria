import { ChartColumnStacked, ChartSpline, GitCompareArrows, MessageSquareShare, User } from "lucide-react"
import { useNavigate } from "react-router"

const HomepageFeaturesComponent = () => {
    const navigate = useNavigate()

    function handleCompareTopicsClick() {
        navigate("/comparison")
    }

    function handleTopicClick() {
        navigate("/topic")
    }

    function handleCategoryClick() {
        navigate("/category")
    } 

    function handleSubredditClick() {
        navigate("/subreddit")
    }

    function handleUserClick() {
        navigate("/user")
    }

    return (
        <section className="flex flex-col bg-[#0f0f0f] w-[49.5%] space-y-[2%] h-[55vh] rounded-2xl p-[1%]">
            <span className='text-gray-400 text-lg pl-4'>Features</span>
            <div className="relative flex items-center px-[2%] h-[15%] w-full bg-[#1d1d1e] space-x-4 rounded-xl">
                <div className='flex items-center justify-center h-[65%] w-[8%] bg-gradient-to-tr from-test1 to-test2 rounded-lg'>
                    <GitCompareArrows className="w-[30px] h-[30px] text-gray-300" strokeWidth={2.5}/>
                </div>
                <div className='flex flex-col space-y-2'>
                    <span>Compare Topics</span>
                    <span className='text-sm font-light'>Compare two topics and view sentiments and trends</span>
                </div>
                <button className='absolute right-4 px-4 py-2 bg-gray-700 rounded-xl' onClick={handleCompareTopicsClick}>View More</button>
            </div>
            <div className="relative flex items-center px-[2%] h-[15%] w-full bg-[#1d1d1e] space-x-4 rounded-xl">
                <div className='flex items-center justify-center h-[65%] w-[8%] bg-gradient-to-tr from-test1 to-test2 rounded-lg'>
                    <MessageSquareShare className="w-[30px] h-[30px] text-gray-300" strokeWidth={2.5}/>
                </div>
                <div className='flex flex-col space-y-2'>
                    <span>Topics Trends</span>
                    <span className='text-sm font-light'>View Sentiments and Trends for a Topic</span>
                </div>
                <button className='absolute right-4 px-4 py-2 bg-gray-700 rounded-xl' onClick={handleTopicClick}>View More</button>
            </div>
            <div className="relative flex items-center px-[2%] h-[15%] w-full bg-[#1d1d1e] space-x-4 rounded-xl">
                <div className='flex items-center justify-center h-[65%] w-[8%] bg-gradient-to-tr from-test1 to-test2 rounded-lg'>
                    <ChartColumnStacked className="w-[30px] h-[30px] text-gray-300" strokeWidth={2.5}/>
                </div>
                <div className='flex flex-col space-y-2'>
                    <span>Category Trends</span>
                    <span className='text-sm font-light'>View Sentiments and Trends for a Category</span>
                </div>
                <button className='absolute right-4 px-4 py-2 bg-gray-700 rounded-xl' onClick={handleCategoryClick}>View More</button>
            </div>
            <div className="relative flex items-center px-[2%] h-[15%] w-full bg-[#1d1d1e] space-x-4 rounded-xl">
                <div className='flex items-center justify-center h-[65%] w-[8%] bg-gradient-to-tr from-test1 to-test2 rounded-lg'>
                    <ChartSpline className="w-[30px] h-[30px] text-gray-300" strokeWidth={2.5}/>
                </div>
                <div className='flex flex-col space-y-2'>
                    <span>Subreddit Trends</span>
                    <span className='text-sm font-light'>View Sentiments and Trends for a Subreddit</span>
                </div>
                <button className='absolute right-4 px-4 py-2 bg-gray-700 rounded-xl' onClick={handleSubredditClick}>View More</button>
            </div>
            <div className="relative flex items-center px-[2%] h-[15%] w-full bg-[#1d1d1e] space-x-4 rounded-xl">
                <div className='flex items-center justify-center h-[65%] w-[8%] bg-gradient-to-tr from-test1 to-test2 rounded-lg'>
                    <User className="w-[30px] h-[30px] text-gray-300" strokeWidth={2.5}/>
                </div>
                <div className='flex flex-col space-y-2'>
                    <span>User Statistics</span>
                    <span className='text-sm font-light'>View Your Most Statistics and Trends (Requires an Account)</span>
                </div>
                <button className='absolute right-4 px-4 py-2 bg-gray-700 rounded-xl' onClick={handleUserClick}>View More</button>
            </div>
        </section>
    )
}

export default HomepageFeaturesComponent