import { DotPattern } from "../ui/magicui/dot-pattern";
import { cn } from "../lib/utils";
import { LoginLogo } from "../components/LoginPageComponents/loginLogo";
import { LoginForm } from "../components/LoginPageComponents/LoginForm";
import { Home } from "lucide-react";
import { Toaster } from "sonner";

export default function LoginPage() {
    
    return (
        <main className="flex justify-center items-center h-[100vh] w-[100vw] bg-background">
            <Toaster />
            <DotPattern
                className={cn(
                "[mask-image:radial-gradient(1300px_circle_at_center,white,transparent)]",
                )}
            />
            <section className="flex flex-col space-y-[2vh] items-center z-10 w-[25vw] h-[55vh] bg-[#141414] rounded-3xl py-[5vh]">
                <LoginLogo />
                <span className="text-3xl font-semibold">Welcome Back</span>
                <span className="text-sm text-gray-400 font-semibold">Don't have an account yet? 
                    <a className="text-transparent bg-clip-text bg-gradient-to-tr from-test1 to-test2 ml-2 font-semibold hover:bg-gradient-to-br" href="/signup">Sign Up!</a>
                </span>
                <LoginForm/>
            </section>

            <a 
                className="fixed flex justify-center items-center bottom-12 right-12 w-12 h-12 bg-card hover:bg-logo rounded-xl border-2 border-interactive"
                href="/"
            >
                <Home/>
            </a>
        </main>
    )
}