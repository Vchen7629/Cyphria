import { LogOut } from 'lucide-react';
import { useLogoutMutation } from '../../api/auth-slices/authApiSlice';
import { useNavigate } from 'react-router';

export function LogoutButton() {
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
        <LogOut className='text-gray-400 w-[30px] h-[30px]' onClick={handleLogout}/>
    )
}