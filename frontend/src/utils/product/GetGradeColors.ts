
/**
 @function

 @description - Helper function to return different background color and text color based
 on the product letter grade (S, A+, A, etc)

 @param {string} grade = The product letter grade
 */
export function getGradeColors(grade: string) {
  if (grade === "S") {
    return { bg: "bg-amber-950/40", text: "text-amber-300" };
  }
  if (grade.startsWith("A")) {
    return { bg: "bg-teal-950/40", text: "text-teal-300" };
  }
  if (grade.startsWith("B")) {
    return { bg: "bg-sky-950/40", text: "text-sky-300" };
  }
  if (grade.startsWith("C")) {
    return { bg: "bg-stone-800/40", text: "text-stone-300" };
  }
  if (grade.startsWith("D")) {
    return { bg: "bg-orange-950/40", text: "text-orange-300" };
  }
  if (grade === "F") {
    return { bg: "bg-red-950/40", text: "text-red-300" };
  }
  return { bg: "bg-zinc-800/40", text: "text-zinc-400" };
};