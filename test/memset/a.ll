target datalayout = "e-m:e-p:64:64-i64:64-i128:128-n32:64-S128"
target triple = "riscv64-unknown-linux-gnu"

%struct.CHpoints = type { i32, %struct.point, i32, ptr, ptr }
%struct.point = type { i32, i32 }

define void @abc(ptr %0, i32 %1, ptr %2, i64 %3, ptr %4) {
  br label %6

6:                                                ; preds = %5
  %7 = getelementptr inbounds %struct.CHpoints, ptr %0, i64 0, i32 3
  %8 = getelementptr inbounds %struct.CHpoints, ptr %0, i64 0, i32 1
  tail call void @llvm.memset.p0.i64(ptr noundef nonnull align 8 dereferenceable(16) %7, i8 0, i64 16, i1 false)
  store i64 %3, ptr %8, align 4
  store i32 %1, ptr %0, align 8
  %9 = load ptr, ptr %2, align 8
  %10 = icmp eq ptr %9, null
  br label %11

11:                                               ; preds = %6
  store i1 %10, ptr %4, align 1
  ret void
}

declare ptr @malloc(i64)

declare i32 @puts(ptr)

; Function Attrs: nocallback nofree nounwind willreturn memory(argmem: write)
declare void @llvm.memset.p0.i64(ptr nocapture writeonly, i8, i64, i1 immarg) #0

attributes #0 = { nocallback nofree nounwind willreturn memory(argmem: write) }
