import { cn } from '../../lib/utils';
import { DotPattern } from '../../ui/magicui/dot-pattern';
import { AnimatedGridPattern } from "../../ui/magicui/animated-grid-pattern";


export function DotPatternBackground() {
    
    return (
        <div className="relative flex h-[500px] w-[100vw] items-center justify-center overflow-hidden rounded-lg bg-transparent p-20">
            <AnimatedGridPattern
                numSquares={30}
                maxOpacity={0.1}
                duration={3}
                repeatDelay={1}
                className={cn(
                "[mask-image:linear-gradient(to_bottom,white,transparent,transparent)] ",
                )}
            />
        </div>
    )
}