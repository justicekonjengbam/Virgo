import { useEffect, useState } from 'react';
import { ActivityIndicator, Pressable, SafeAreaView, ScrollView, StyleSheet, View } from 'react-native';
import MaterialCommunityIcons from 'react-native-vector-icons/MaterialCommunityIcons';

import { DsCard, DsText } from '../../../components/design-system';
import { AppPageHeader } from '../../../components/navigation/AppPageHeader';
import { apiClient } from '../../../services/apiClient';
import { colors, radius, spacing } from '../../../theme';

type NotificationItem = { id:number; notification_type:string; title:string; body:string; read_at:string|null; created_at:string };

export function NotificationsScreen({ onBack, onMenuPress }: { onBack:()=>void; onMenuPress:()=>void }) {
  const [items,setItems]=useState<NotificationItem[]|null>(null); const [error,setError]=useState('');
  useEffect(()=>{ void apiClient.get<NotificationItem[]>('/api/v1/passengers/me/notifications').then(response=>setItems(response.data)).catch(cause=>setError(cause instanceof Error?cause.message:'Unable to load notifications.')); },[]);
  const read=async(item:NotificationItem)=>{ if(item.read_at)return; const updated=(await apiClient.patch<NotificationItem>(`/api/v1/passengers/me/notifications/${item.id}/read`)).data; setItems(current=>current?.map(value=>value.id===item.id?updated:value)??null); };
  return <SafeAreaView style={styles.safe}><AppPageHeader onBack={onBack} onMenuPress={onMenuPress} title="Notifications"/><ScrollView contentContainerStyle={styles.content}>{error?<DsText color={colors.error}>{error}</DsText>:null}{items===null?<ActivityIndicator color={colors.primary}/>:items.length?items.map(item=><Pressable key={item.id} onPress={()=>void read(item)}><DsCard elevated={!item.read_at} style={[styles.card,!item.read_at&&styles.unread]}><View style={styles.icon}><MaterialCommunityIcons color={colors.primary} name={item.notification_type.includes('driver_assigned')?'account-check':item.notification_type.includes('confirmed')?'check-decagram':'bell-outline'} size={25}/></View><View style={styles.copy}><DsText variant="bodyMedium">{item.title}</DsText><DsText color={colors.textSecondary} variant="caption">{item.body}</DsText><DsText color={colors.textTertiary} variant="caption">{new Date(item.created_at).toLocaleString('en-IN')}</DsText></View>{!item.read_at?<View style={styles.dot}/>:null}</DsCard></Pressable>):<DsCard style={styles.empty}><MaterialCommunityIcons color={colors.textTertiary} name="bell-sleep-outline" size={38}/><DsText color={colors.textSecondary}>No notifications yet.</DsText></DsCard>}</ScrollView></SafeAreaView>;
}
const styles=StyleSheet.create({safe:{backgroundColor:colors.background,flex:1},content:{gap:spacing.md,padding:spacing.xl},card:{alignItems:'center',flexDirection:'row',gap:spacing.md,padding:spacing.md},unread:{backgroundColor:colors.primarySoft,borderColor:colors.primary,borderWidth:1},icon:{alignItems:'center',backgroundColor:colors.surface,borderRadius:radius.md,height:46,justifyContent:'center',width:46},copy:{flex:1,gap:spacing.xxs},dot:{backgroundColor:colors.primary,borderRadius:radius.pill,height:9,width:9},empty:{alignItems:'center',gap:spacing.md,padding:spacing.xxl}});
