name := "enhanced-ai-recommendation"

version := "2.0.0"

scalaVersion := "2.12.15"

organization := "com.example.recommendation"

// Spark依赖
val sparkVersion = "3.3.0"
val hadoopVersion = "3.3.4"

libraryDependencies ++= Seq(
  // Spark核心
  "org.apache.spark" %% "spark-core" % sparkVersion % "provided",
  "org.apache.spark" %% "spark-sql" % sparkVersion % "provided",
  "org.apache.spark" %% "spark-mllib" % sparkVersion % "provided",
  "org.apache.spark" %% "spark-streaming" % sparkVersion % "provided",
  
  // Hadoop
  "org.apache.hadoop" % "hadoop-client" % hadoopVersion % "provided",
  "org.apache.hadoop" % "hadoop-common" % hadoopVersion % "provided",
  "org.apache.hadoop" % "hadoop-hdfs" % hadoopVersion % "provided",
  
  // 数据库连接
  "mysql" % "mysql-connector-java" % "8.0.33",
  
  // JSON处理
  "com.fasterxml.jackson.core" % "jackson-core" % "2.13.4",
  "com.fasterxml.jackson.core" % "jackson-databind" % "2.13.4",
  "com.fasterxml.jackson.module" %% "jackson-module-scala" % "2.13.4",
  
  // 机器学习
  "org.apache.spark" %% "spark-ml" % sparkVersion % "provided",
  
  // 工具类
  "org.scalaj" %% "scalaj-http" % "2.4.2",
  "com.typesafe" % "config" % "1.4.2",
  
  // 测试
  "org.scalatest" %% "scalatest" % "3.2.15" % "test",
  "org.scalacheck" %% "scalacheck" % "1.17.0" % "test"
)

// 编译选项
scalacOptions ++= Seq(
  "-deprecation",
  "-encoding", "UTF-8",
  "-feature",
  "-language:existentials",
  "-language:higherKinds",
  "-language:implicitConversions",
  "-unchecked",
  "-Xfatal-warnings",
  "-Xlint",
  "-Yno-adapted-args",
  "-Ywarn-dead-code",
  "-Ywarn-numeric-widen",
  "-Ywarn-value-discard",
  "-Ywarn-unused-import",
  "-Ywarn-unused"
)

// JVM选项
javaOptions ++= Seq(
  "-Xmx4g",
  "-XX:+UseG1GC",
  "-XX:MaxGCPauseMillis=200"
)

// 资源文件
Compile / resourceDirectory := baseDirectory.value / "src" / "main" / "resources"
Test / resourceDirectory := baseDirectory.value / "src" / "test" / "resources"

// 打包配置
assembly / assemblyJarName := "enhanced-ai-recommendation.jar"
assembly / assemblyMergeStrategy := {
  case PathList("META-INF", xs @ _*) => MergeStrategy.discard
  case x => MergeStrategy.first
}

// 排除冲突的依赖
assembly / assemblyExcludedJars := {
  val cp = (Compile / fullClasspath).value
  cp.filter { file =>
    file.data.getName.contains("spark-core") ||
    file.data.getName.contains("spark-sql") ||
    file.data.getName.contains("spark-mllib") ||
    file.data.getName.contains("hadoop-common") ||
    file.data.getName.contains("hadoop-hdfs")
  }
}

// 测试配置
Test / parallelExecution := false
Test / fork := true

// 发布配置
publishMavenStyle := true
publishTo := Some(Resolver.file("local", file("target/repository")))

// 插件
addCompilerPlugin("org.typelevel" %% "kind-projector" % "0.13.2" cross CrossVersion.full)

// 项目信息
description := "Enhanced AI Recommendation System - 真正发挥AI价值的推荐系统"
homepage := Some(url("https://github.com/example/enhanced-ai-recommendation"))
licenses := Seq("Apache-2.0" -> url("https://www.apache.org/licenses/LICENSE-2.0"))
developers := List(
  Developer("ai-team", "AI Team", "ai-team@example.com", url("https://github.com/ai-team"))
)

// 构建信息
buildInfoKeys := Seq[BuildInfoKey](
  name,
  version,
  scalaVersion,
  sbtVersion,
  "sparkVersion" -> sparkVersion,
  "hadoopVersion" -> hadoopVersion,
  "buildTime" -> java.time.Instant.now().toString
)
buildInfoPackage := "com.example.recommendation"
enablePlugins(BuildInfoPlugin)


