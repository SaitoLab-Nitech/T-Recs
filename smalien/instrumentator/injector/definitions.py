
# PERMISSION_WRITE_EXTERNAL_STORAGE = '<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>'
PERMISSION_WRITE_EXTERNAL_STORAGE_FOR_ENCODED_XML = 'android:name="android.permission.WRITE_EXTERNAL_STORAGE"'
PERMISSION_WRITE_EXTERNAL_STORAGE_FOR_DECODED_XML = '<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"/>'

SMALIEN_CLASS_HEADER_TEMPLATE = '''
.class public {}
.super Ljava/lang/Object;
'''

SMALIEN_WRITER_SMALI_NAME = 'SmalienWriter.smali'
SMALIEN_WRITER_CLASS_NAME = 'LSmalienWriter;'

SMALIEN_WRITER = '''
# static fields
.field private static bufferedWriter:Ljava/io/BufferedWriter; = null

.field private static cntr:I = 0x0

.field private static final file:Ljava/io/File;


.field private static head:I = 0x0


.field private static final printWriter:Ljava/io/PrintWriter;

.field private static final size:I = 0xc350

.field private static stringArray:[Ljava/lang/String;


# direct methods
.method static constructor <clinit>()V
    .locals 4

    .line 32
    new-instance v0, Ljava/io/File;

    const-string v1, "LOG_PATH"

    invoke-direct {v0, v1}, Ljava/io/File;-><init>(Ljava/lang/String;)V

    sput-object v0, LSmalienWriter;->file:Ljava/io/File;

    const/4 v1, 0x1

    .line 34
    :try_start_0
    new-instance v2, Ljava/io/BufferedWriter;

    new-instance v3, Ljava/io/FileWriter;

    invoke-direct {v3, v0, v1}, Ljava/io/FileWriter;-><init>(Ljava/io/File;Z)V

    invoke-direct {v2, v3}, Ljava/io/BufferedWriter;-><init>(Ljava/io/Writer;)V

    sput-object v2, LSmalienWriter;->bufferedWriter:Ljava/io/BufferedWriter;
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    .line 37
    :catch_0
    new-instance v0, Ljava/io/PrintWriter;

    sget-object v2, LSmalienWriter;->bufferedWriter:Ljava/io/BufferedWriter;

    invoke-direct {v0, v2, v1}, Ljava/io/PrintWriter;-><init>(Ljava/io/Writer;Z)V

    sput-object v0, LSmalienWriter;->printWriter:Ljava/io/PrintWriter;

    const/4 v0, 0x0

    .line 43
    sput v0, LSmalienWriter;->head:I

    .line 44
    sput v0, LSmalienWriter;->cntr:I

    const v0, 0xc350

    new-array v0, v0, [Ljava/lang/String;

    .line 45
    sput-object v0, LSmalienWriter;->stringArray:[Ljava/lang/String;

    return-void
.end method

.method public constructor <init>()V
    .locals 0

    .line 14
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method public static writeTag(Ljava/lang/String;)V
    .locals 6

    .line 49
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v0

    .line 50
    invoke-static {}, Landroid/os/Process;->myPid()I

    move-result v2

    .line 51
    invoke-static {}, Landroid/os/Process;->myTid()I

    move-result v3

    .line 52
    new-instance v4, Ljava/lang/StringBuilder;

    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v4, v0, v1}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, ":"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, ":"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v3}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, ":"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    invoke-static {p0}, Lorg/json/JSONObject;->quote(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p0

    .line 57
    sget-object v0, LSmalienWriter;->stringArray:[Ljava/lang/String;

    monitor-enter v0

    .line 58
    :try_start_0
    sget-object v1, LSmalienWriter;->stringArray:[Ljava/lang/String;

    sget v2, LSmalienWriter;->head:I

    sget v3, LSmalienWriter;->cntr:I

    add-int v4, v2, v3

    const v5, 0xc350

    rem-int/2addr v4, v5

    aput-object p0, v1, v4

    add-int/lit8 v3, v3, 0x1

    .line 59
    sput v3, LSmalienWriter;->cntr:I

    const/16 p0, LOG_BUFF_SIZE

    const/4 v4, 0x0

    if-lt v3, p0, :cond_0

    add-int p0, v2, v3

    .line 64
    rem-int/2addr p0, v5

    sput p0, LSmalienWriter;->head:I

    .line 65
    sput v4, LSmalienWriter;->cntr:I

    goto :goto_0

    :cond_0
    move v2, v4

    move v3, v2

    .line 67
    :goto_0
    monitor-exit v0
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    if-eqz v3, :cond_2

    .line 70
    new-array p0, v3, [Ljava/lang/String;

    add-int v0, v2, v3

    if-gt v0, v5, :cond_1

    .line 72
    invoke-static {v1, v2, p0, v4, v3}, Ljava/lang/System;->arraycopy(Ljava/lang/Object;ILjava/lang/Object;II)V

    goto :goto_1

    :cond_1
    sub-int/2addr v5, v2

    .line 76
    invoke-static {v1, v2, p0, v4, v5}, Ljava/lang/System;->arraycopy(Ljava/lang/Object;ILjava/lang/Object;II)V

    .line 77
    sget-object v0, LSmalienWriter;->stringArray:[Ljava/lang/String;

    sub-int/2addr v3, v5

    invoke-static {v0, v4, p0, v5, v3}, Ljava/lang/System;->arraycopy(Ljava/lang/Object;ILjava/lang/Object;II)V

    .line 79
    :goto_1
    sget-object v0, LSmalienWriter;->printWriter:Ljava/io/PrintWriter;

    invoke-static {p0}, Ljava/util/Arrays;->toString([Ljava/lang/Object;)Ljava/lang/String;

    move-result-object p0

    invoke-virtual {v0, p0}, Ljava/io/PrintWriter;->println(Ljava/lang/String;)V

    :cond_2
    return-void

    :catchall_0
    move-exception p0

    .line 67
    :try_start_1
    monitor-exit v0
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    throw p0
.end method

.method public static writeVal(Ljava/lang/String;Ljava/lang/String;)V
    .locals 5

    .line 95
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v0

    .line 96
    invoke-static {}, Landroid/os/Process;->myPid()I

    move-result v2

    .line 97
    invoke-static {}, Landroid/os/Process;->myTid()I

    move-result v3

    .line 98
    new-instance v4, Ljava/lang/StringBuilder;

    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v4, v0, v1}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, ":"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, ":"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v3}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, ":"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    const-string v0, ":"

    invoke-virtual {p0, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    invoke-static {p0}, Lorg/json/JSONObject;->quote(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p0

    .line 103
    sget-object p1, LSmalienWriter;->stringArray:[Ljava/lang/String;

    monitor-enter p1

    .line 104
    :try_start_0
    sget-object v0, LSmalienWriter;->stringArray:[Ljava/lang/String;

    sget v1, LSmalienWriter;->head:I

    sget v2, LSmalienWriter;->cntr:I

    add-int v3, v1, v2

    const v4, 0xc350

    rem-int/2addr v3, v4

    aput-object p0, v0, v3

    add-int/lit8 v2, v2, 0x1

    .line 105
    sput v2, LSmalienWriter;->cntr:I

    const/16 p0, LOG_BUFF_SIZE

    const/4 v3, 0x0

    if-lt v2, p0, :cond_0

    add-int p0, v1, v2

    .line 110
    rem-int/2addr p0, v4

    sput p0, LSmalienWriter;->head:I

    .line 111
    sput v3, LSmalienWriter;->cntr:I

    goto :goto_0

    :cond_0
    move v1, v3

    move v2, v1

    .line 113
    :goto_0
    monitor-exit p1
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    if-eqz v2, :cond_2

    .line 116
    new-array p0, v2, [Ljava/lang/String;

    add-int p1, v1, v2

    if-gt p1, v4, :cond_1

    .line 118
    invoke-static {v0, v1, p0, v3, v2}, Ljava/lang/System;->arraycopy(Ljava/lang/Object;ILjava/lang/Object;II)V

    goto :goto_1

    :cond_1
    sub-int/2addr v4, v1

    .line 122
    invoke-static {v0, v1, p0, v3, v4}, Ljava/lang/System;->arraycopy(Ljava/lang/Object;ILjava/lang/Object;II)V

    .line 123
    sget-object p1, LSmalienWriter;->stringArray:[Ljava/lang/String;

    sub-int/2addr v2, v4

    invoke-static {p1, v3, p0, v4, v2}, Ljava/lang/System;->arraycopy(Ljava/lang/Object;ILjava/lang/Object;II)V

    .line 125
    :goto_1
    sget-object p1, LSmalienWriter;->printWriter:Ljava/io/PrintWriter;

    invoke-static {p0}, Ljava/util/Arrays;->toString([Ljava/lang/Object;)Ljava/lang/String;

    move-result-object p0

    invoke-virtual {p1, p0}, Ljava/io/PrintWriter;->println(Ljava/lang/String;)V

    :cond_2
    return-void

    :catchall_0
    move-exception p0

    .line 113
    :try_start_1
    monitor-exit p1
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    throw p0
.end method
'''
