/** @type {import('tailwindcss').Config} */
import tailwindcssAnimate from "tailwindcss-animate";

export default {
    darkMode: ["class"],
    content: [
      "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
  	extend: {
  		fontFamily: {
  			roboto: [
  				'Roboto',
  				'sans-serif'
  			]
  		},
  		backgroundImage: {
  			background: 'linear-gradient(180deg, #0a0a0a 0%, rgba(0, 0, 1, .13) 8%, rgb(3, 4, 10) 40%, rgb(5, 6, 16) 100%);'
  		},
  		backgroundSize: {
  			'homepage-radial-gold': '100px 150px'
  		},
  		borderRadius: {
  			lg: 'var(--radius)',
  			md: 'calc(var(--radius) - 2px)',
  			sm: 'calc(var(--radius) - 4px)'
  		},
  		colors: {
  			gold: {
  				DEFAULT: '#ffd700'
  			},
  			goldenrod: '#daa520',
  			'background': '#131314',
			'bordercolor': '#333333',
			'interactive': '#005F7F',
			'test1': '#0a0f23',
			'test2': '#060a16',
  		},
  		boxShadow: {
  			custom: 'inset 2px 2px 4px rgba(0,0,0,0.6), inset -2px -2px 4px rgba(255,255,255,0.02);',
  			mycards: '0px 0px 15px rgb(19, 18, 18)',
  			dropdow: '0 0px 4px 0px hsl(var(--shadow-color))',
  			'inner-border': 'inset 0 0 0 4px rgba(55, 65, 81, 1)'
  		},
  		keyframes: {
  			pulse: {
  				'0%': {
  					transform: 'translate(-50%, -50%) scale(0)',
  					opacity: '0.5'
  				},
  				'100%': {
  					transform: 'translate(-50%, -50%) scale(1)',
  					opacity: '0'
  				}
  			},
  			skFoldCube: {
  				'0%, 10%': {
  					transform: 'perspective(140px) rotateX(-180deg)',
  					opacity: '0'
  				},
  				'25%, 75%': {
  					transform: 'perspective(140px) rotateX(0deg)',
  					opacity: '1'
  				},
  				'90%, 100%': {
  					transform: 'perspective(140px) rotateY(180deg)',
  					opacity: '0'
  				}
  			},
  			marquee: {
  				from: {
  					transform: 'translateX(0)'
  				},
  				to: {
  					transform: 'translateX(calc(-100% - var(--gap)))'
  				}
  			},
  			'marquee-vertical': {
  				from: {
  					transform: 'translateY(0)'
  				},
  				to: {
  					transform: 'translateY(calc(-100% - var(--gap)))'
  				}
  			},
  			'accordion-down': {
  				from: {
  					height: '0'
  				},
  				to: {
  					height: 'var(--radix-accordion-content-height)'
  				}
  			},
  			'accordion-up': {
  				from: {
  					height: 'var(--radix-accordion-content-height)'
  				},
  				to: {
  					height: '0'
  				}
  			},
  			'fade-in-up': {
  				'0%': {
  					opacity: '0',
  					transform: 'translateY(10px)'
  				},
  				'100%': {
  					opacity: '1',
  					transform: 'translateY(0)'
  				}
  			}
  		},
  		animation: {
  			marquee: 'marquee var(--duration) infinite linear',
  			'marquee-vertical': 'marquee-vertical var(--duration) linear infinite',
  			skFoldCube: 'skFoldCube 2.4s infinite linear both',
  			'accordion-down': 'accordion-down 0.2s ease-out',
  			'accordion-up': 'accordion-up 0.2s ease-out',
  			pulse: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) forwards',
  			'fade-in-up': 'fade-in-up 0.3s ease-out forwards'
  		}
  	}
  },
  plugins: [tailwindcssAnimate, require("tailwindcss-animate")],
}

