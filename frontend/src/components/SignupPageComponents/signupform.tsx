import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { Button } from "../../ui/shadcn/button"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "../../ui/shadcn/form"
import { Input } from "../../ui/shadcn/input"
import { useSignUpMutation } from "../../app/auth-slices/authApiSlice"
import { useNavigate } from "react-router"
import { toast } from "sonner"
import { setCredentials } from "../../app/state/authstate"
import { useDispatch } from "react-redux"

const formSchema = z.object({
    username: z.string().min(2, {
        message: "Username must be at least 2 characters"
    }),
    password: z.string().min(3, {
        message: "Please enter a valid password (at least 3 characters)"
    })
})

const SignUpForm = () =>{
    const [SignUp] = useSignUpMutation()
    const navigate = useNavigate()
    const dispatch = useDispatch()

    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        defaultValues: {
          username: "",
          password: ""
        },
    }) 
    
    function onSubmit(values: z.infer<typeof formSchema>) {
        const promise = SignUp({
            username: values.username,
            password: values.password
        }).unwrap();
        toast.promise(promise, {
            loading: "loading...",
            success: () => {
                dispatch(setCredentials({username: values.username}))
                navigate("/")
                return "Successfully Signed Up!"
            },
            error: (error) => {
                if (error?.status === 404) {
                    return error?.data?.message || "Invalid Username or Password";
                } else {
                    return "An unexpected error occurred";
                }
            },
        })
    }

    return (
        <Form {...form} >
            <form id="login-form" onSubmit={form.handleSubmit(onSubmit)} className="flex flex-col  w-[85%] space-y-4 pb-4">
                <FormField
                    control={form.control}
                    name="username"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Username</FormLabel>
                            <FormControl>
                                <Input className="border-bordercolor border-2 rounded-sm" type="string" placeholder="enter username" {...field} />
                            </FormControl>
                            <FormMessage/>
                        </FormItem>
                    )}
                />
                <FormField
                    control={form.control}
                    name="password"
                    render={({ field }) => (
                        <FormItem>
                            <FormLabel>Password</FormLabel>
                            <FormControl>
                                <Input className="border-bordercolor border-2 rounded-sm" type="password" placeholder="enter password" {...field} />
                            </FormControl>
                            <FormMessage/>
                        </FormItem>
                    )}
                />
            </form>
            <Button type="submit" form="login-form" className=" bg-blue-400 w-[85%] rounded-md hover:bg-blue-300">Sign Up</Button>
        </Form>
    )
}

export default SignUpForm