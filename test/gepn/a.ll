target datalayout = "e-m:e-p:64:64-i64:64-i128:128-n32:64-S128"
target triple = "riscv64-unknown-linux-gnu"

define void @abc(ptr %0) {
newFuncRoot:
  br label %entry

entry:                                            ; preds = %newFuncRoot
  %arrayidx1 = getelementptr inbounds i8, ptr %0, i64 8
  %1 = load double, ptr %arrayidx1, align 8, !tbaa !0
  %arrayidx2 = getelementptr inbounds i8, ptr %0, i64 32
  %2 = load double, ptr %arrayidx2, align 8, !tbaa !0
  store double %2, ptr %arrayidx1, align 8, !tbaa !0
  store double %1, ptr %arrayidx2, align 8, !tbaa !0
  %arrayidx9 = getelementptr inbounds i8, ptr %0, i64 16
  %3 = load double, ptr %arrayidx9, align 8, !tbaa !0
  %arrayidx10 = getelementptr inbounds i8, ptr %0, i64 64
  %4 = load double, ptr %arrayidx10, align 8, !tbaa !0
  store double %4, ptr %arrayidx9, align 8, !tbaa !0
  store double %3, ptr %arrayidx10, align 8, !tbaa !0
  %arrayidx17 = getelementptr inbounds i8, ptr %0, i64 48
  %5 = load double, ptr %arrayidx17, align 8, !tbaa !0
  %arrayidx19 = getelementptr inbounds i8, ptr %0, i64 72
  %6 = load double, ptr %arrayidx19, align 8, !tbaa !0
  store double %6, ptr %arrayidx17, align 8, !tbaa !0
  store double %5, ptr %arrayidx19, align 8, !tbaa !0
  %arrayidx25 = getelementptr inbounds i8, ptr %0, i64 88
  %7 = load double, ptr %arrayidx25, align 8, !tbaa !0
  %arrayidx26 = getelementptr inbounds i8, ptr %0, i64 96
  %arrayidx27 = getelementptr inbounds i8, ptr %0, i64 112
  %8 = load double, ptr %arrayidx27, align 8, !tbaa !0
  store double %8, ptr %arrayidx25, align 8, !tbaa !0
  store double %7, ptr %arrayidx27, align 8, !tbaa !0
  %9 = load double, ptr %arrayidx26, align 8, !tbaa !0
  %arrayidx35 = getelementptr inbounds i8, ptr %0, i64 24
  %10 = load double, ptr %arrayidx35, align 8, !tbaa !0
  store double %10, ptr %arrayidx26, align 8, !tbaa !0
  store double %9, ptr %arrayidx35, align 8, !tbaa !0
  %arrayidx41 = getelementptr inbounds i8, ptr %0, i64 104
  %11 = load double, ptr %arrayidx41, align 8, !tbaa !0
  %arrayidx43 = getelementptr inbounds i8, ptr %0, i64 56
  %12 = load double, ptr %arrayidx43, align 8, !tbaa !0
  store double %12, ptr %arrayidx41, align 8, !tbaa !0
  store double %11, ptr %arrayidx43, align 8, !tbaa !0
  br label %exit.exitStub

exit.exitStub:                                    ; preds = %entry
  ret void
}

!0 = !{!1, !1, i64 0}
!1 = !{!"double", !2, i64 0}
!2 = !{!"omnipotent char", !3, i64 0}
!3 = !{!"Simple C++ TBAA"}
