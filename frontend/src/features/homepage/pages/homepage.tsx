import { useSelector } from 'react-redux';
import { SidebarComponent } from '../../../features/navigation/components/sidebar';
import { selectExpandState } from '../../../app/state/ui';
import { HeaderComponent } from '../../../shared/components/header';
import HomepageFeaturesComponent from '../components/featuresComponent';

export default function Homepage() {
    const expand = useSelector(selectExpandState)

    return (
        <main className="flex w-[100vw] h-[100vh] bg-background p-[1vw]">
            <SidebarComponent/>
            <div className={`flex flex-col ${expand ? "w-[88%] px-[3%]" : "w-[95vw] px-[3%]"} font-bold  overflow-auto`}>
                <HeaderComponent/>
                <section className="flex mt-[5vh] items-center justify-between w-full">
                    <div className='flex flex-col space-y-1'>
                        <span className='text-3xl text-transparent bg-clip-text font-extrabold bg-gradient-to-r from-test1 to-test2'>Welcome to Cyphria</span>
                        <span className='text-gray-400 font-semibold'>Reddit Sentiment and Trend Analysis Platform</span>
                    </div>
                    
                </section>
                <main className='flex space-x-[1%] mt-[5vh]'>
                    <HomepageFeaturesComponent />
                    <section className="flex flex-col bg-[#0f0f0f] w-[49.5%] space-y-[2%] h-[50vh] rounded-2xl p-[1%]">
                        <span className='text-gray-400 text-lg pl-4'>Statistics</span>
                        <div className="relative flex flex-col px-[2%] h-[50%] w-full bg-[#1d1d1e] space-x-4 rounded-xl">
                            <span className='text-gray-400 text-lg font-light pt-2'>Trending Topics - top 5 most Searched Topics</span>
                        </div>
                    </section>
                </main>
            </div>
        </main>
    )
}