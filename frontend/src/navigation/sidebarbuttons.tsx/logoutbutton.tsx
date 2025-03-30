import { LogOut } from 'lucide-react';
import { useLogoutMutation } from '../../api/auth-slices/authApiSlice';
import { useNavigate } from 'react-router';
import { expand } from './types';

export function LogoutButton({ expand }: expand) {
    const navigate = useNavigate()
    const [logout, {isSuccess, isError}] = useLogoutMutation()

    async function handleLogout() {
        try {
            await logout({}).unwrap();
            if (isSuccess) {
                navigate("/")
            } else if (isError) {
                console.error("error sending logout request to api")
            }
        } catch {
            console.error("error with something")
        }
    }
    return (
        <button className={`${expand ? "flex items-center space-x-4" : "flex flex-col"}`} onClick={handleLogout}>
            <LogOut className='text-gray-400 w-[30px] h-[30px]'/>
            {expand && (
                <h1 className="font-bold text-gray-300 font-bold text-gray-300 hover:text-transparent hover:bg-clip-text hover:bg-gradient-to-r hover:from-test1 hover:to-test2">Logout</h1>
            )}
        </button>
    )
}