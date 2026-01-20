import { Monitor, Headphones, Smartphone, Gamepad2, Camera, Home, Laptop, Cpu, Keyboard, Speaker} from "lucide-react";

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
    Laptop,
    Cpu,
    Monitor,
    Keyboard,
    Speaker,
    Headphones,
    Smartphone,
    Gamepad2,
    Camera,
    Home,
};

export default iconMap