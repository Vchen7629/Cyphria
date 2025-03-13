import { ChartLine } from 'lucide-react';
import { HeaderComponent } from '../components/header/header';
import HomepageHeader from '../components/header/homepageheader';
import { SidebarComponent } from '../components/sidebar';

export default function Homepage() {

    return (
        <main className="flex flex-col space-y-[5vh] py-[5vh] items-center w-[100vw] h-[100vh] bg-background">
            <HomepageHeader/>
            <section className="flex w-full h-[60vh]  items-center font-bold">
                <div className='w-1/2'>

                </div>
                <div className="flex pl-[4vw] w-1/2 text-5xl">
                    <span className='text-gray-400 w-[60%] leading-[1.5]'>Data Driven Social Media Sentiment Analysis platform </span>
                </div>
            </section>
        </main>
    )
}